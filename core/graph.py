"""Graph utilities for lumen-atlas.

The graph prioritizes topology over geometry. Nodes are lightweight data
objects that can be exported directly to JSON, while edge sets capture
multiple overlapping relationships (wiring, surface proximity, semantic
regions). Geometry and embeddings are derived, never authoritative.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, MutableMapping, Optional, Set


@dataclass
class LEDNode:
    """A single LED node with human-readable metadata.

    All fields are designed to be JSON-serializable and easy to review in
    plain text. The `neighbors` dict indexes adjacency lists by edge set
    name (e.g. "strip" for wiring, "surface" for perceptual proximity).
    """

    id: int
    chunk_id: str
    index_in_chunk: int
    atlas_uv: Dict[str, float]
    region: Optional[str] = None
    neighbors: MutableMapping[str, List[int]] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    description: Optional[str] = None
    confidence: Optional[float] = None
    camera_observations: List[Dict[str, float]] = field(default_factory=list)

    def add_neighbor(self, edge_set: str, neighbor_id: int) -> None:
        """Attach a neighbor id to the given edge set.

        Edge sets stay explicit so it remains clear whether a connection
        comes from wiring, surface proximity, or semantic grouping.
        """

        adjacency = self.neighbors.setdefault(edge_set, [])
        if neighbor_id not in adjacency:
            adjacency.append(neighbor_id)


class AtlasGraph:
    """Graph of LED nodes with multiple edge sets.

    Internally stores nodes in a dictionary keyed by id, with adjacency
    maintained per edge set to keep wiring separate from surface or
    semantic relationships.
    """

    def __init__(self) -> None:
        self.nodes: Dict[int, LEDNode] = {}
        self.edge_sets: Dict[str, Dict[int, Set[int]]] = {}

    def add_node(self, node: LEDNode) -> None:
        """Register a node in the atlas graph.

        The node's neighbor lists are mirrored into the internal edge set
        adjacency maps so query utilities can operate efficiently.
        """

        self.nodes[node.id] = node
        for edge_set, neighbors in node.neighbors.items():
            for neighbor_id in neighbors:
                self.add_edge(node.id, neighbor_id, edge_set=edge_set)

    def add_edge(self, a: int, b: int, *, edge_set: str = "surface", bidirectional: bool = True) -> None:
        """Add an edge between two node ids for the named edge set.

        By default edges are bidirectional, matching how we typically think
        about proximity on deformable surfaces.
        """

        adjacency = self.edge_sets.setdefault(edge_set, {})
        adjacency.setdefault(a, set()).add(b)
        if bidirectional:
            adjacency.setdefault(b, set()).add(a)

    def neighbors(self, node_id: int, *, edge_set: str = "surface") -> List[int]:
        """Return neighbors of a node for a given edge set."""

        adjacency = self.edge_sets.get(edge_set, {})
        return sorted(adjacency.get(node_id, set()))

    def edge_set_names(self) -> List[str]:
        """List available edge sets."""

        return sorted(self.edge_sets.keys())

    def nodes_in_region(self, region: str) -> List[LEDNode]:
        """Return nodes tagged with a given semantic region."""

        return [node for node in self.nodes.values() if node.region == region]

    def add_edge_set_from_pairs(self, pairs: Iterable[tuple[int, int]], *, edge_set: str, bidirectional: bool = True) -> None:
        """Bulk-add an edge set from iterable pairs."""

        for a, b in pairs:
            self.add_edge(a, b, edge_set=edge_set, bidirectional=bidirectional)

    def to_serializable(self) -> Dict[str, object]:
        """Export a minimal JSON-serializable representation of the graph."""

        nodes_payload: List[Dict[str, object]] = []
        for node in self.nodes.values():
            nodes_payload.append({
                "id": node.id,
                "chunk_id": node.chunk_id,
                "index_in_chunk": node.index_in_chunk,
                "region": node.region,
                "atlas_uv": node.atlas_uv,
                "neighbors": {name: sorted(ids) for name, ids in node.neighbors.items()},
                "tags": node.tags,
                "description": node.description,
                "confidence": node.confidence,
                "camera_observations": node.camera_observations,
            })
        return {"nodes": nodes_payload, "edge_sets": self.edge_set_names()}


def from_serializable(data: Dict[str, object]) -> AtlasGraph:
    """Create an AtlasGraph from a serialized atlas structure.

    The input is expected to align with the JSON schemas under `schema/`.
    Unknown keys on nodes are preserved in the data classes via direct
    assignment to keep human annotations intact.
    """

    graph = AtlasGraph()
    raw_nodes = data.get("nodes", [])
    for item in raw_nodes:
        if not isinstance(item, dict):
            continue
        node = LEDNode(
            id=int(item.get("id")),
            chunk_id=str(item.get("chunk_id")),
            index_in_chunk=int(item.get("index_in_chunk")),
            atlas_uv=dict(item.get("atlas_uv", {})),
            region=item.get("region"),
            neighbors=dict(item.get("neighbors", {})),
            tags=list(item.get("tags", [])),
            description=item.get("description"),
            confidence=item.get("confidence"),
            camera_observations=list(item.get("camera_observations", [])),
        )
        graph.add_node(node)
    return graph
