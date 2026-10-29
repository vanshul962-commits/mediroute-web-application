"""Dijkstra's Shortest Path Algorithm for MediRoute.

This module provides a pure, self-contained implementation of Dijkstra's algorithm
for emergency vehicle routing over weighted road networks. It operates directly
on adjacency lists and does NOT rely on external shortest-path solvers.

Theoretical Foundations:
- Problem: Single-Source Shortest Path (SSSP) on a non-negatively weighted graph G = (V, E).
- Paradigm: Greedy algorithm with optimal substructure. At each step, the algorithm
  greedily finalizes the shortest distance to the unvisited node with minimum tentative distance.
- Data Structures:
  - Adjacency list representation: G[u] = [(v, weight, ...)]
  - Min-Priority Queue (Binary Heap via heapq): extracts minimum tentative distance node in O(log V).
  - Distance Table: dist[u] = tentative shortest distance from source to u.
  - Predecessor Table: pred[u] = predecessor node on the shortest path for backtracking.
  - Finalized Set: closed set tracking nodes whose minimal distance is locked in.

Complexity:
- Time Complexity: O((|V| + |E|) log |V|) when implemented with an adjacency list and binary min-heap.
  - Each vertex is extracted from the min-heap at most once: |V| * O(log |V|).
  - Each directed edge (u, v) is relaxed at most once: |E| * O(log |V|) for heap updates/pushes.
- Space Complexity: O(|V| + |E|) to maintain graph structures, distance dictionaries, and the heap.

Graph vs Straight-Line Distance:
- Straight-line (Euclidean) distance: sqrt((x2 - x1)^2 + (y2 - y1)^2) represents spatial proximity
  as the crow flies, ignoring road topology, obstacles, one-way streets, traffic limits, and river crossings.
- Graph shortest-path distance: Computes the actual traversable road route, factoring in real turn
  constraints, variable speed limits, intersection delays, and bridge locations.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from algorithms.priority_queue import PriorityQueue


@dataclass
class DijkstraResult:
    """Structured result returned by Dijkstra shortest-path calculations."""

    source: str
    destination: str
    path: List[str] = field(default_factory=list)
    total_cost: float = float("inf")
    explored_nodes: int = 0
    execution_time_ms: float = 0.0
    found: bool = False
    error: Optional[str] = None
    distances: Dict[str, float] = field(default_factory=dict)
    predecessors: Dict[str, Optional[str]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to a serializable dictionary."""
        return {
            "source": self.source,
            "destination": self.destination,
            "path": self.path,
            "total_cost": self.total_cost if self.found else None,
            "explored_nodes": self.explored_nodes,
            "execution_time_ms": round(self.execution_time_ms, 4),
            "found": self.found,
            "error": self.error,
        }


def validate_graph_weights(adjacency: Dict[str, List[Any]]) -> None:
    """Validate that all edge weights in the adjacency list are non-negative.

    Args:
        adjacency: Mapping from node IDs to lists of outgoing edges.
                   Edges may be tuples `(neighbor, weight)` or dicts with a 'weight'/'travel_time' key.

    Raises:
        ValueError: If any edge has a negative weight.
    """
    for node, edges in adjacency.items():
        for edge in edges:
            weight = _extract_weight(edge)
            if weight < 0:
                raise ValueError(
                    f"Dijkstra algorithm requires non-negative edge weights. "
                    f"Found negative weight {weight} on edge from '{node}'."
                )


def _extract_weight(edge: Any) -> float:
    """Extract numeric weight from an edge representation (tuple or dict)."""
    if isinstance(edge, (tuple, list)):
        return float(edge[1])
    if isinstance(edge, dict):
        if "travel_time" in edge:
            return float(edge["travel_time"])
        if "weight" in edge:
            return float(edge["weight"])
        if "cost" in edge:
            return float(edge["cost"])
        raise KeyError("Edge dict must contain 'travel_time', 'weight', or 'cost' key")
    raise TypeError(f"Unsupported edge type: {type(edge)}")


def _extract_target(edge: Any) -> str:
    """Extract destination node ID from an edge representation."""
    if isinstance(edge, (tuple, list)):
        return str(edge[0])
    if isinstance(edge, dict):
        if "to" in edge:
            return str(edge["to"])
        if "destination" in edge:
            return str(edge["destination"])
        if "target" in edge:
            return str(edge["target"])
        raise KeyError("Edge dict must contain 'to', 'destination', or 'target' key")
    raise TypeError(f"Unsupported edge type: {type(edge)}")


def dijkstra_shortest_path(
    adjacency: Dict[str, List[Any]],
    source: str,
    destination: str,
    early_exit: bool = True,
) -> DijkstraResult:
    """Compute the shortest path from source to destination using Dijkstra's algorithm.

    Args:
        adjacency: Adjacency list mapping node_id -> list of edges.
                   Each edge can be (neighbor, weight) or dict(to=..., travel_time=...).
        source: Node ID where the route starts.
        destination: Node ID where the route ends.
        early_exit: If True, halts search immediately upon popping the destination node.

    Returns:
        DijkstraResult containing the optimal path, cost, runtime, and exploration stats.
    """
    t_start = time.perf_counter()

    # 1. Input Validation
    if source not in adjacency:
        t_end = time.perf_counter()
        return DijkstraResult(
            source=source,
            destination=destination,
            found=False,
            error=f"Source node '{source}' does not exist in graph",
            execution_time_ms=(t_end - t_start) * 1000.0,
        )

    if destination not in adjacency:
        t_end = time.perf_counter()
        return DijkstraResult(
            source=source,
            destination=destination,
            found=False,
            error=f"Destination node '{destination}' does not exist in graph",
            execution_time_ms=(t_end - t_start) * 1000.0,
        )

    # 2. Check for negative weights across the graph
    try:
        validate_graph_weights(adjacency)
    except ValueError as err:
        t_end = time.perf_counter()
        return DijkstraResult(
            source=source,
            destination=destination,
            found=False,
            error=str(err),
            execution_time_ms=(t_end - t_start) * 1000.0,
        )

    # 3. Handle Trivial Case: Source == Destination
    if source == destination:
        t_end = time.perf_counter()
        return DijkstraResult(
            source=source,
            destination=destination,
            path=[source],
            total_cost=0.0,
            explored_nodes=1,
            execution_time_ms=(t_end - t_start) * 1000.0,
            found=True,
            distances={source: 0.0},
            predecessors={source: None},
        )

    # 4. Initialize Data Structures
    distances: Dict[str, float] = {node: float("inf") for node in adjacency}
    distances[source] = 0.0

    predecessors: Dict[str, Optional[str]] = {node: None for node in adjacency}
    finalized: Set[str] = set()
    explored_nodes_count = 0

    pq: PriorityQueue[str] = PriorityQueue()
    pq.push(source, 0.0)

    # 5. Core Dijkstra Relaxation Loop
    while not pq.is_empty():
        current_node, current_dist = pq.pop()

        # If already finalized with a shorter distance, ignore duplicate heap entry
        if current_node in finalized:
            continue

        finalized.add(current_node)
        explored_nodes_count += 1

        # Early termination: When destination is finalized, its shortest path is guaranteed optimal
        if early_exit and current_node == destination:
            break

        # If current tentative distance is infinite, remaining nodes are unreachable
        if current_dist == float("inf"):
            break

        # Edge relaxation
        for edge in adjacency.get(current_node, []):
            neighbor = _extract_target(edge)
            weight = _extract_weight(edge)

            # Skip already finalized nodes (greedy invariant: distance is already minimal)
            if neighbor in finalized:
                continue

            new_distance = current_dist + weight
            if new_distance < distances.get(neighbor, float("inf")):
                distances[neighbor] = new_distance
                predecessors[neighbor] = current_node
                pq.push(neighbor, new_distance)

    t_end = time.perf_counter()
    exec_time_ms = (t_end - t_start) * 1000.0

    # 6. Check Reachability & Path Reconstruction
    dest_distance = distances.get(destination, float("inf"))
    if dest_distance == float("inf") or destination not in finalized and predecessors[destination] is None:
        return DijkstraResult(
            source=source,
            destination=destination,
            path=[],
            total_cost=float("inf"),
            explored_nodes=explored_nodes_count,
            execution_time_ms=exec_time_ms,
            found=False,
            error=f"No traversable road path exists from '{source}' to '{destination}'",
            distances=distances,
            predecessors=predecessors,
        )

    # Backtrack path from destination to source
    path: List[str] = []
    curr: Optional[str] = destination
    while curr is not None:
        path.append(curr)
        if curr == source:
            break
        curr = predecessors.get(curr)

    path.reverse()

    # Integrity verification: Path must start at source
    if not path or path[0] != source:
        return DijkstraResult(
            source=source,
            destination=destination,
            path=[],
            total_cost=float("inf"),
            explored_nodes=explored_nodes_count,
            execution_time_ms=exec_time_ms,
            found=False,
            error="Failed to reconstruct valid path (disconnected components)",
            distances=distances,
            predecessors=predecessors,
        )

    return DijkstraResult(
        source=source,
        destination=destination,
        path=path,
        total_cost=round(dest_distance, 3),
        explored_nodes=explored_nodes_count,
        execution_time_ms=exec_time_ms,
        found=True,
        error=None,
        distances=distances,
        predecessors=predecessors,
    )


def compute_all_pairs_sample(
    adjacency: Dict[str, List[Any]],
    sample_pairs: List[Tuple[str, str]],
) -> List[DijkstraResult]:
    """Execute Dijkstra across a batch of source-destination pairs for benchmarking.

    Args:
        adjacency: Adjacency list of the road network.
        sample_pairs: List of (source, destination) node tuples.

    Returns:
        List of DijkstraResult objects with execution statistics.
    """
    results: List[DijkstraResult] = []
    for src, dst in sample_pairs:
        res = dijkstra_shortest_path(adjacency, src, dst)
        results.append(res)
    return results
