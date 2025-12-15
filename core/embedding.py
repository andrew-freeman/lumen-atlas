"""Derived embeddings for visualization.

Embeddings are optional and never treated as ground truth. They provide a
stable view for debugging and effect prototyping while respecting the
underlying topology-first representation.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from .graph import AtlasGraph, LEDNode


def atlas_uv_positions(graph: AtlasGraph) -> Dict[int, Tuple[float, float]]:
    """Return a mapping from node id to atlas UV coordinates.

    The atlas UV space is assumed to be stable but abstract; downstream
    renderers can use this to seed layout or interpolation.
    """

    positions: Dict[int, Tuple[float, float]] = {}
    for node in graph.nodes.values():
        u = float(node.atlas_uv.get("u", 0.0))
        v = float(node.atlas_uv.get("v", 0.0))
        positions[node.id] = (u, v)
    return positions


def barycenter(graph: AtlasGraph, node_ids: List[int]) -> Tuple[float, float]:
    """Compute a simple barycenter in atlas UV space for the provided nodes."""

    if not node_ids:
        return 0.0, 0.0
    coords = atlas_uv_positions(graph)
    total_u = sum(coords.get(node_id, (0.0, 0.0))[0] for node_id in node_ids)
    total_v = sum(coords.get(node_id, (0.0, 0.0))[1] for node_id in node_ids)
    count = len(node_ids)
    return total_u / count, total_v / count


def path_to_polyline(graph: AtlasGraph, path: List[int]) -> List[Tuple[float, float]]:
    """Convert a path of node ids into a polyline in atlas UV space."""

    coords = atlas_uv_positions(graph)
    return [coords[node_id] for node_id in path if node_id in coords]
