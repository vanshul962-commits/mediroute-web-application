"""Unit tests for Dijkstra's shortest path algorithm."""

import pytest
from algorithms.dijkstra import dijkstra_shortest_path, validate_graph_weights


@pytest.fixture
def sample_graph():
    """Build a standard test graph with multiple alternative routes:

    A --- (1) ---> B --- (2) ---> D
    |                            ^
    +------------ (5) -----------+
    |                            |
    +--- (2) ---> C --- (1) -----+
    """
    return {
        "A": [("B", 1.0), ("C", 2.0), ("D", 5.0)],
        "B": [("D", 2.0)],
        "C": [("D", 1.0)],
        "D": [],
    }


def test_dijkstra_simple_shortest_path(sample_graph):
    """Path from A to D:
    Path 1: A -> D (cost 5)
    Path 2: A -> B -> D (cost 1 + 2 = 3)
    Path 3: A -> C -> D (cost 2 + 1 = 3)
    Shortest cost should be 3.0.
    """
    res = dijkstra_shortest_path(sample_graph, "A", "D")
    assert res.found is True
    assert res.total_cost == 3.0
    assert res.path in [["A", "B", "D"], ["A", "C", "D"]]
    assert res.explored_nodes > 0
    assert res.execution_time_ms >= 0.0


def test_dijkstra_cost_vs_hop_count():
    """Verify Dijkstra chooses lower cost over fewer hops.
    Direct path: X -> Z (cost 10)
    Multi-hop: X -> Y1 -> Y2 -> Z (cost 1 + 1 + 1 = 3)
    """
    graph = {
        "X": [("Z", 10.0), ("Y1", 1.0)],
        "Y1": [("Y2", 1.0)],
        "Y2": [("Z", 1.0)],
        "Z": [],
    }
    res = dijkstra_shortest_path(graph, "X", "Z")
    assert res.found is True
    assert res.total_cost == 3.0
    assert res.path == ["X", "Y1", "Y2", "Z"]


def test_dijkstra_source_equals_destination():
    """Verify source == destination returns cost 0 and single-element path."""
    graph = {"A": [("B", 4.0)], "B": []}
    res = dijkstra_shortest_path(graph, "A", "A")
    assert res.found is True
    assert res.total_cost == 0.0
    assert res.path == ["A"]
    assert res.explored_nodes == 1


def test_dijkstra_unreachable_destination():
    """Verify behavior when no path exists between components."""
    graph = {
        "A": [("B", 2.0)],
        "B": [],
        "C": [("D", 1.0)],
        "D": [],
    }
    res = dijkstra_shortest_path(graph, "A", "D")
    assert res.found is False
    assert res.path == []
    assert res.total_cost == float("inf")
    assert res.error is not None
    assert "No traversable road path" in res.error


def test_dijkstra_unknown_nodes():
    """Verify appropriate error handling for non-existent source or destination."""
    graph = {"A": [("B", 1.0)], "B": []}

    res_src = dijkstra_shortest_path(graph, "NON_EXISTENT", "B")
    assert res_src.found is False
    assert "Source node 'NON_EXISTENT' does not exist" in (res_src.error or "")

    res_dst = dijkstra_shortest_path(graph, "A", "NON_EXISTENT")
    assert res_dst.found is False
    assert "Destination node 'NON_EXISTENT' does not exist" in (res_dst.error or "")


def test_dijkstra_negative_edge_weight_rejection():
    """Verify that negative edge weights are strictly rejected."""
    neg_graph = {
        "A": [("B", -2.5)],
        "B": [],
    }
    with pytest.raises(ValueError, match="negative weight"):
        validate_graph_weights(neg_graph)

    res = dijkstra_shortest_path(neg_graph, "A", "B")
    assert res.found is False
    assert "negative weight" in (res.error or "").lower()


def test_dijkstra_zero_weight_edge():
    """Verify that zero-weight edges are processed correctly without infinite loops."""
    zero_graph = {
        "A": [("B", 0.0)],
        "B": [("C", 3.0)],
        "C": [],
    }
    res = dijkstra_shortest_path(zero_graph, "A", "C")
    assert res.found is True
    assert res.total_cost == 3.0
    assert res.path == ["A", "B", "C"]
