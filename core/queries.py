"""Common graph queries for atlas navigation.

Queries are intentionally topology-first: they operate on edge sets and
semantic tags instead of assuming Euclidean geometry.
"""

from __future__ import annotations

from collections import deque
from typing import Iterable, Iterator, List, Set

from .graph import AtlasGraph, LEDNode


def nodes_with_tag(graph: AtlasGraph, tag: str) -> List[LEDNode]:
    """Return all nodes containing a given tag."""

    return [node for node in graph.nodes.values() if tag in node.tags]


def breadth_first_traverse(graph: AtlasGraph, start: int, *, edge_set: str = "surface", max_depth: int | None = None) -> Iterator[int]:
    """Traverse the graph in breadth-first order from a starting node.

    BFS is constrained to the chosen edge set to keep wiring traversal
    distinct from surface traversal.
    """

    visited: Set[int] = set()
    queue: deque[tuple[int, int]] = deque([(start, 0)])
    while queue:
        node_id, depth = queue.popleft()
        if node_id in visited:
            continue
        visited.add(node_id)
        yield node_id

        next_depth = depth + 1
        if max_depth is not None and next_depth > max_depth:
            continue

        for neighbor in graph.neighbors(node_id, edge_set=edge_set):
            if neighbor not in visited:
                queue.append((neighbor, next_depth))


def shortest_hop_path(graph: AtlasGraph, start: int, goal: int, *, edge_set: str = "surface") -> List[int]:
    """Return the shortest hop path between two nodes using BFS.

    This intentionally ignores geometric distances and focuses solely on
    hop count within the specified edge set.
    """

    if start == goal:
        return [start]

    visited: Set[int] = {start}
    queue: deque[list[int]] = deque([[start]])

    while queue:
        path = queue.popleft()
        current = path[-1]
        for neighbor in graph.neighbors(current, edge_set=edge_set):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            new_path = path + [neighbor]
            if neighbor == goal:
                return new_path
            queue.append(new_path)
    return []


def walk_region_boundary(graph: AtlasGraph, region_names: Iterable[str]) -> List[int]:
    """Find nodes that sit on the boundary between the provided regions.

    A node is considered a boundary if at least one neighbor belongs to a
    different region within the provided set. The result is unique and
    stable for use in effect targeting.
    """

    targets: Set[int] = set()
    region_lookup = set(region_names)
    for node in graph.nodes.values():
        if node.region not in region_lookup:
            continue
        for neighbor_id in graph.neighbors(node.id, edge_set="surface"):
            neighbor = graph.nodes.get(neighbor_id)
            if neighbor and neighbor.region in region_lookup and neighbor.region != node.region:
                targets.add(node.id)
                break
    return sorted(targets)
