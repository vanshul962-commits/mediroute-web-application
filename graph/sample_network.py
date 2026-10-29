"""Sample Road Network Definitions for MediRoute.

Defines:
1. `build_default_metro_network`: 20-node realistic metropolitan grid with ambulance
   stations, trauma centers, downtown intersections, and expressway corridors.
2. `build_disconnected_network`: Network with two disconnected partitions for testing
   unreachable destination handling in Dijkstra and dispatch engines.
3. `generate_random_network`: Deterministic seeded procedural network generator for
   algorithm scaling and benchmarking.
"""

from __future__ import annotations
import json
import math
import os
import random
from typing import Dict, List, Tuple

from graph.graph_utils import RoadNetwork


def build_default_metro_network() -> RoadNetwork:
    """Build the canonical 20-node metropolitan emergency network.

    Features:
    - 3 Ambulance Stations (Alpha, Beta, Gamma) strategically situated.
    - 3 Hospitals (City General, St. Jude Trauma, Westside Medical).
    - 14 Road Intersections representing key commercial, industrial, and suburban hubs.
    - Realistically weighted travel times (e.g. Expressways allow 2x speed compared to congested downtown).
    """
    net = RoadNetwork(name="Metro Central Emergency Grid")

    # 1. Ambulance Stations (3)
    net.add_node("STA_ALPHA", "Station Alpha (North)", "station", x=22.0, y=82.0, zone="North")
    net.add_node("STA_BETA", "Station Beta (Harbor)", "station", x=86.0, y=28.0, zone="East")
    net.add_node("STA_GAMMA", "Station Gamma (West River)", "station", x=16.0, y=24.0, zone="West")

    # 2. Hospitals & Trauma Centers (3)
    net.add_node("HOSP_CENTRAL", "City General Hospital", "hospital", x=52.0, y=56.0, zone="Central")
    net.add_node("HOSP_TRAUMA", "St. Jude Trauma Center", "hospital", x=82.0, y=82.0, zone="North-East")
    net.add_node("HOSP_WEST", "Westside Community Clinic", "hospital", x=24.0, y=44.0, zone="West")

    # 3. Intersections & Urban Landmarks (14)
    net.add_node("INT_NORTH_GATE", "North Gate Avenue", "intersection", x=36.0, y=88.0, zone="North")
    net.add_node("INT_UNIVERSITY", "University Campus Gate", "intersection", x=32.0, y=66.0, zone="North-West")
    net.add_node("INT_INDUSTRIAL", "Industrial Logistics Park", "intersection", x=14.0, y=62.0, zone="West")
    net.add_node("INT_RIVER_CROSS", "River Bridge Crossing", "intersection", x=36.0, y=48.0, zone="Central-West")
    net.add_node("INT_DOWNTOWN", "Downtown Central Plaza", "intersection", x=50.0, y=42.0, zone="Central")
    net.add_node("INT_MIDTOWN", "Midtown Crossway", "intersection", x=56.0, y=68.0, zone="Central")
    net.add_node("INT_EAST_MALL", "Metro Shopping Promenade", "intersection", x=68.0, y=72.0, zone="East")
    net.add_node("INT_HIGHWAY_RAMP", "Highway 101 Onramp", "intersection", x=68.0, y=48.0, zone="Central-East")
    net.add_node("INT_TECH_PARK", "Tech District Sector 4", "intersection", x=78.0, y=46.0, zone="East")
    net.add_node("INT_HARBOR_VIEW", "Harbor Promenade", "intersection", x=72.0, y=24.0, zone="East")
    net.add_node("INT_AIRPORT_RD", "Airport Express Junction", "intersection", x=84.0, y=14.0, zone="South-East")
    net.add_node("INT_SOUTH_CIRCLE", "South Park Circle", "intersection", x=50.0, y=18.0, zone="South")
    net.add_node("INT_OLD_TOWN", "Historic Old Town", "intersection", x=38.0, y=28.0, zone="South-West")
    net.add_node("INT_SUBURB_SOUTH", "Meadowbrook Suburbs", "intersection", x=28.0, y=14.0, zone="South")

    # 4. Roads / Edges with simulated travel times (minutes) and road names
    # North Sector
    net.add_edge("STA_ALPHA", "INT_NORTH_GATE", travel_time=3.2, distance_km=2.4, road_name="Northway Blvd")
    net.add_edge("STA_ALPHA", "INT_UNIVERSITY", travel_time=4.1, distance_km=3.0, road_name="Academic Parkway")
    net.add_edge("INT_NORTH_GATE", "INT_MIDTOWN", travel_time=4.8, distance_km=4.2, road_name="Northern Arterial")
    net.add_edge("INT_NORTH_GATE", "HOSP_TRAUMA", travel_time=6.5, distance_km=6.0, road_name="Trauma Expressway")
    net.add_edge("INT_MIDTOWN", "HOSP_TRAUMA", travel_time=5.0, distance_km=4.5, road_name="Northeast Highway")
    net.add_edge("INT_MIDTOWN", "INT_EAST_MALL", travel_time=3.0, distance_km=2.2, road_name="Mall Access Road")
    net.add_edge("INT_EAST_MALL", "HOSP_TRAUMA", travel_time=3.5, distance_km=2.8, road_name="St. Jude Drive")

    # Central & Hospital Core
    net.add_edge("INT_UNIVERSITY", "INT_MIDTOWN", travel_time=4.5, distance_km=4.0, road_name="Midtown Tunnel")
    net.add_edge("INT_MIDTOWN", "HOSP_CENTRAL", travel_time=2.1, distance_km=1.5, road_name="Hospital Way")
    net.add_edge("HOSP_CENTRAL", "INT_DOWNTOWN", travel_time=2.5, distance_km=1.8, road_name="Civic Center Ave")
    net.add_edge("HOSP_CENTRAL", "INT_HIGHWAY_RAMP", travel_time=3.2, distance_km=2.7, road_name="Hwy 101 Spur")
    net.add_edge("INT_DOWNTOWN", "INT_HIGHWAY_RAMP", travel_time=3.0, distance_km=2.5, road_name="Downtown Arterial")
    net.add_edge("INT_UNIVERSITY", "HOSP_WEST", travel_time=3.8, distance_km=3.2, road_name="West Campus Lane")

    # West Sector
    net.add_edge("STA_GAMMA", "INT_SUBURB_SOUTH", travel_time=3.0, distance_km=2.2, road_name="Riverfront Drive")
    net.add_edge("STA_GAMMA", "INT_OLD_TOWN", travel_time=4.0, distance_km=3.1, road_name="Canal Road")
    net.add_edge("STA_GAMMA", "HOSP_WEST", travel_time=3.5, distance_km=2.8, road_name="West Health Parkway")
    net.add_edge("HOSP_WEST", "INT_INDUSTRIAL", travel_time=3.2, distance_km=2.5, road_name="Industrial Bypass")
    net.add_edge("INT_INDUSTRIAL", "INT_UNIVERSITY", travel_time=3.7, distance_km=3.0, road_name="West Perimeter Rd")
    net.add_edge("HOSP_WEST", "INT_RIVER_CROSS", travel_time=2.6, distance_km=1.9, road_name="River Bridge West")
    net.add_edge("INT_RIVER_CROSS", "INT_DOWNTOWN", travel_time=2.8, distance_km=2.0, road_name="Grand River Bridge")
    net.add_edge("INT_RIVER_CROSS", "INT_OLD_TOWN", travel_time=3.4, distance_km=2.6, road_name="Heritage Way")

    # East Sector & Highway 101 Expressway
    net.add_edge("INT_EAST_MALL", "INT_TECH_PARK", travel_time=4.2, distance_km=3.8, road_name="Innovation Blvd")
    net.add_edge("INT_HIGHWAY_RAMP", "INT_TECH_PARK", travel_time=2.0, distance_km=2.2, road_name="Hwy 101 East Corridor")
    net.add_edge("INT_TECH_PARK", "STA_BETA", travel_time=3.1, distance_km=2.6, road_name="Harbor Access Rd")
    net.add_edge("INT_TECH_PARK", "INT_HARBOR_VIEW", travel_time=3.4, distance_km=2.8, road_name="Bayside Ave")
    net.add_edge("STA_BETA", "INT_HARBOR_VIEW", travel_time=2.2, distance_km=1.8, road_name="Pier View Street")
    net.add_edge("STA_BETA", "INT_AIRPORT_RD", travel_time=2.8, distance_km=2.4, road_name="Maritime Drive")

    # South Sector & Airport Corridor
    net.add_edge("INT_HARBOR_VIEW", "INT_AIRPORT_RD", travel_time=2.6, distance_km=2.1, road_name="Coastline Blvd")
    net.add_edge("INT_AIRPORT_RD", "INT_SOUTH_CIRCLE", travel_time=5.2, distance_km=5.5, road_name="Airport Express Highway")
    net.add_edge("INT_SOUTH_CIRCLE", "INT_DOWNTOWN", travel_time=4.0, distance_km=3.6, road_name="South Main St")
    net.add_edge("INT_SOUTH_CIRCLE", "INT_OLD_TOWN", travel_time=2.9, distance_km=2.2, road_name="Parkway South")
    net.add_edge("INT_OLD_TOWN", "INT_SUBURB_SOUTH", travel_time=2.5, distance_km=1.9, road_name="Meadow Lane")
    net.add_edge("INT_SUBURB_SOUTH", "INT_SOUTH_CIRCLE", travel_time=3.8, distance_km=3.2, road_name="Southern Connector")

    return net


def build_disconnected_network() -> RoadNetwork:
    """Build a network with two isolated components for testing unreachable routing."""
    net = RoadNetwork(name="Disconnected Test Network")
    # Component 1 (Mainland)
    net.add_node("C1_NODE_A", "Mainland Station", "station", x=20.0, y=50.0)
    net.add_node("C1_NODE_B", "Mainland Crossing", "intersection", x=40.0, y=50.0)
    net.add_edge("C1_NODE_A", "C1_NODE_B", travel_time=4.0, road_name="Mainland Road")

    # Component 2 (Isolated Island - No bridge exists)
    net.add_node("C2_NODE_X", "Island Clinic", "hospital", x=70.0, y=50.0)
    net.add_node("C2_NODE_Y", "Island Incident Site", "incident", x=90.0, y=50.0)
    net.add_edge("C2_NODE_X", "C2_NODE_Y", travel_time=3.0, road_name="Island Perimeter")

    return net


def generate_random_network(seed: int = 42, num_nodes: int = 25, connectivity: float = 0.25) -> RoadNetwork:
    """Generate a procedural, deterministic road network for benchmarking algorithms.

    Args:
        seed: Random seed for deterministic reproducibility.
        num_nodes: Total count of nodes to create (between 10 and 100).
        connectivity: Target edge density factor.

    Returns:
        A connected RoadNetwork instance.
    """
    rng = random.Random(seed)
    net = RoadNetwork(name=f"Synthetic Network (N={num_nodes}, Seed={seed})")

    # Generate nodes with coordinates in 100x100 space
    node_ids: List[str] = []
    for i in range(num_nodes):
        nid = f"N_{i+1:02d}"
        node_ids.append(nid)
        ntype = "intersection"
        if i == 0:
            ntype = "station"
        elif i == 1:
            ntype = "hospital"
        elif i % 7 == 0:
            ntype = "station"
        elif i % 9 == 0:
            ntype = "hospital"

        x = rng.uniform(5.0, 95.0)
        y = rng.uniform(5.0, 95.0)
        net.add_node(nid, f"Node {nid}", node_type=ntype, x=x, y=y)

    # Ensure network is connected by constructing a spanning backbone
    for i in range(num_nodes - 1):
        u = node_ids[i]
        v = node_ids[i + 1]
        dist = math.hypot(net.nodes[u].x - net.nodes[v].x, net.nodes[u].y - net.nodes[v].y)
        travel_time = max(1.0, round(dist * 0.12 + rng.uniform(0.5, 2.0), 2))
        net.add_edge(u, v, travel_time=travel_time, distance_km=round(dist * 0.1, 2), road_name=f"Link {u}-{v}")

    # Add additional edges based on connectivity factor and distance proximity
    for i in range(num_nodes):
        for j in range(i + 2, num_nodes):
            u = node_ids[i]
            v = node_ids[j]
            dist = math.hypot(net.nodes[u].x - net.nodes[v].x, net.nodes[u].y - net.nodes[v].y)
            # Connect if close and within probability
            if dist < 45.0 and rng.random() < connectivity:
                travel_time = max(1.0, round(dist * 0.12 + rng.uniform(0.5, 2.0), 2))
                net.add_edge(u, v, travel_time=travel_time, distance_km=round(dist * 0.1, 2), road_name=f"Link {u}-{v}")

    return net


def save_default_network_json(filepath: str) -> None:
    """Save the default metro network to a JSON file."""
    net = build_default_metro_network()
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(net.to_dict(), f, indent=2)
