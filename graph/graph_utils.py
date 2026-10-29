"""Graph Data Structures and Utilities for MediRoute Road Networks.

This module provides the core `RoadNetwork` class, handling adjacency list
representations, validation, node/edge lookups, JSON export/import, and
random network generation for benchmarking.
"""

from __future__ import annotations
import json
import math
import random
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class RoadNode:
    """Represents a location/junction within the synthetic road network."""

    id: str
    label: str
    node_type: str  # "station", "hospital", "intersection", "incident"
    x: float
    y: float
    zone: str = "Central"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RoadEdge:
    """Represents a traversable road segment connecting two nodes."""

    u: str
    v: str
    travel_time: float  # weight in simulated minutes
    distance_km: float
    road_name: str
    bidirectional: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RoadNetwork:
    """Adjacency list representation of a simulated emergency road network."""

    def __init__(self, name: str = "Metro City Grid") -> None:
        self.name: str = name
        self.nodes: Dict[str, RoadNode] = {}
        # Adjacency list: node_id -> list of edge dicts:
        # [{"to": v, "travel_time": t, "distance_km": d, "road_name": name, "edge_id": ...}]
        self.adjacency: Dict[str, List[Dict[str, Any]]] = {}
        self.edges: List[RoadEdge] = []

    def add_node(
        self,
        node_id: str,
        label: str,
        node_type: str = "intersection",
        x: float = 0.0,
        y: float = 0.0,
        zone: str = "Central",
    ) -> RoadNode:
        """Add or update a node in the network."""
        node = RoadNode(
            id=node_id,
            label=label,
            node_type=node_type,
            x=round(float(x), 2),
            y=round(float(y), 2),
            zone=zone,
        )
        self.nodes[node_id] = node
        if node_id not in self.adjacency:
            self.adjacency[node_id] = []
        return node

    def add_edge(
        self,
        u: str,
        v: str,
        travel_time: float,
        distance_km: Optional[float] = None,
        road_name: Optional[str] = None,
        bidirectional: bool = True,
    ) -> None:
        """Add a directed or undirected road between u and v."""
        if u not in self.nodes:
            raise KeyError(f"Source node '{u}' not found in network")
        if v not in self.nodes:
            raise KeyError(f"Target node '{v}' not found in network")
        if travel_time < 0:
            raise ValueError(f"Negative travel time ({travel_time}) is not allowed")

        if distance_km is None:
            # Estimate Euclidean distance from coordinates if not provided
            node_u = self.nodes[u]
            node_v = self.nodes[v]
            distance_km = round(
                math.sqrt((node_u.x - node_v.x) ** 2 + (node_u.y - node_v.y) ** 2) * 0.1,
                2,
            )

        if road_name is None:
            road_name = f"{self.nodes[u].label} - {self.nodes[v].label} Connector"

        edge_obj = RoadEdge(
            u=u,
            v=v,
            travel_time=round(float(travel_time), 2),
            distance_km=round(float(distance_km), 2),
            road_name=road_name,
            bidirectional=bidirectional,
        )
        self.edges.append(edge_obj)

        # Forward edge in adjacency list
        self.adjacency[u].append(
            {
                "to": v,
                "travel_time": edge_obj.travel_time,
                "distance_km": edge_obj.distance_km,
                "road_name": edge_obj.road_name,
                "bidirectional": bidirectional,
            }
        )

        # Reverse edge if bidirectional
        if bidirectional:
            self.adjacency[v].append(
                {
                    "to": u,
                    "travel_time": edge_obj.travel_time,
                    "distance_km": edge_obj.distance_km,
                    "road_name": edge_obj.road_name,
                    "bidirectional": bidirectional,
                }
            )

    def get_node(self, node_id: str) -> Optional[RoadNode]:
        """Retrieve a node by its ID."""
        return self.nodes.get(node_id)

    def get_neighbors(self, node_id: str) -> List[Dict[str, Any]]:
        """Get outgoing edges from node_id."""
        return self.adjacency.get(node_id, [])

    def get_node_degree(self, node_id: str) -> int:
        """Return the outgoing degree of a node."""
        return len(self.adjacency.get(node_id, []))

    def node_ids(self) -> List[str]:
        """Return list of all node IDs sorted for determinism."""
        return sorted(list(self.nodes.keys()))

    def stations(self) -> List[str]:
        """Return node IDs of all ambulance stations."""
        return [nid for nid, node in self.nodes.items() if node.node_type == "station"]

    def hospitals(self) -> List[str]:
        """Return node IDs of all hospitals."""
        return [nid for nid, node in self.nodes.items() if node.node_type == "hospital"]

    def intersections(self) -> List[str]:
        """Return node IDs of all standard road intersections."""
        return [
            nid for nid, node in self.nodes.items() if node.node_type == "intersection"
        ]

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate network consistency: non-negative weights, existing endpoints, connectivity."""
        issues: List[str] = []
        if not self.nodes:
            issues.append("Network contains zero nodes.")
            return False, issues

        # Check edge endpoints and weights
        for u, edge_list in self.adjacency.items():
            if u not in self.nodes:
                issues.append(f"Adjacency source '{u}' is not registered as a node.")
            for e in edge_list:
                v = e["to"]
                if v not in self.nodes:
                    issues.append(f"Edge from '{u}' points to non-existent node '{v}'.")
                if e["travel_time"] < 0:
                    issues.append(
                        f"Edge from '{u}' to '{v}' has negative travel time ({e['travel_time']})."
                    )

        # Check isolated nodes
        isolated = [nid for nid in self.nodes if len(self.adjacency.get(nid, [])) == 0]
        if isolated:
            issues.append(f"Network has {len(isolated)} isolated node(s) with no outgoing roads: {isolated}")

        is_valid = len(issues) == 0 or (len(issues) == 1 and "isolated" in issues[0])
        return is_valid, issues

    def to_dict(self) -> Dict[str, Any]:
        """Serialize road network to a JSON-compatible dictionary."""
        return {
            "name": self.name,
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RoadNetwork:
        """Construct RoadNetwork from serialized dictionary."""
        net = cls(name=data.get("name", "Imported Road Network"))
        for n_data in data.get("nodes", []):
            net.add_node(
                node_id=n_data["id"],
                label=n_data["label"],
                node_type=n_data.get("node_type", "intersection"),
                x=n_data.get("x", 0.0),
                y=n_data.get("y", 0.0),
                zone=n_data.get("zone", "Central"),
            )
        for e_data in data.get("edges", []):
            net.add_edge(
                u=e_data["u"],
                v=e_data["v"],
                travel_time=e_data["travel_time"],
                distance_km=e_data.get("distance_km"),
                road_name=e_data.get("road_name"),
                bidirectional=e_data.get("bidirectional", True),
            )
        return net
