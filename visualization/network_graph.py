"""Interactive Plotly Road Network Visualizer for MediRoute.

Renders rich, responsive 2D topological road networks with station markers,
hospital icons, active ambulance badges, incident callouts, and highlighted
Dijkstra shortest paths with alternative candidate routes.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Set, Tuple
import plotly.graph_objects as go

from graph.graph_utils import RoadNetwork
from simulation.ambulances import Ambulance
from simulation.incidents import Incident

NODE_STYLE_MAP = {
    "station": {
        "color": "#0F9D92",      # MediRoute Teal
        "symbol": "square",
        "size": 17,
        "name": "Ambulance Station",
    },
    "hospital": {
        "color": "#0F172A",      # Navy Dark
        "symbol": "cross",
        "size": 18,
        "name": "Hospital / Trauma Center",
    },
    "intersection": {
        "color": "#64748B",      # Slate Gray
        "symbol": "circle",
        "size": 10,
        "name": "Road Intersection",
    },
    "incident": {
        "color": "#DC2626",      # Emergency Red
        "symbol": "diamond",
        "size": 20,
        "name": "Emergency Call",
    },
}


def build_network_figure(
    network: RoadNetwork,
    ambulances: Optional[Dict[str, Ambulance]] = None,
    incidents: Optional[Dict[str, Incident]] = None,
    highlight_route: Optional[List[str]] = None,
    candidate_routes: Optional[List[Tuple[List[str], str]]] = None,
    selected_source: Optional[str] = None,
    selected_target: Optional[str] = None,
    title: str = "",
    height: int = 460,
) -> go.Figure:
    """Generate a properly-scaled, readable, and responsive Plotly road network graph."""
    fig = go.Figure()

    # Calculate optimal dynamic coordinate bounds to prevent cropping
    xs = [n.x for n in network.nodes.values()] if network.nodes else [0, 100]
    ys = [n.y for n in network.nodes.values()] if network.nodes else [0, 100]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    pad_x = max(10.0, (max_x - min_x) * 0.12)
    pad_y = max(12.0, (max_y - min_y) * 0.14)

    # 1. Base Road Network Edges
    edge_x: List[Optional[float]] = []
    edge_y: List[Optional[float]] = []
    edge_hover_x: List[float] = []
    edge_hover_y: List[float] = []
    edge_hover_text: List[str] = []

    drawn_edges: Set[Tuple[str, str]] = set()

    for edge in network.edges:
        u_node = network.get_node(edge.u)
        v_node = network.get_node(edge.v)
        if not u_node or not v_node:
            continue

        pair_key = (min(edge.u, edge.v), max(edge.u, edge.v))
        if pair_key in drawn_edges:
            continue
        drawn_edges.add(pair_key)

        edge_x.extend([u_node.x, v_node.x, None])
        edge_y.extend([u_node.y, v_node.y, None])

        # Midpoint for hover tooltip
        mid_x = (u_node.x + v_node.x) / 2.0
        mid_y = (u_node.y + v_node.y) / 2.0
        edge_hover_x.append(mid_x)
        edge_hover_y.append(mid_y)
        edge_hover_text.append(
            f"<b>{edge.road_name}</b><br>"
            f"Segment: {u_node.label} ↔ {v_node.label}<br>"
            f"Simulated Travel: {edge.travel_time:.1f} min &bull; {edge.distance_km:.1f} km"
        )

    # Road line trace
    fig.add_trace(
        go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(color="#CBD5E1", width=1.8),
            hoverinfo="none",
            name="Road Network",
            showlegend=False,
        )
    )

    # Segment midpoints for hover
    fig.add_trace(
        go.Scatter(
            x=edge_hover_x,
            y=edge_hover_y,
            mode="markers",
            marker=dict(size=5, color="#94A3B8", opacity=0.35),
            hoverinfo="text",
            hovertext=edge_hover_text,
            name="Road Details",
            showlegend=False,
        )
    )

    # 2. Alternative Candidate Routes (Dashed amber lines)
    if candidate_routes:
        for idx, (c_route, label) in enumerate(candidate_routes):
            if not c_route or len(c_route) < 2:
                continue
            cand_x: List[Optional[float]] = []
            cand_y: List[Optional[float]] = []
            for node_id in c_route:
                node = network.get_node(node_id)
                if node:
                    cand_x.append(node.x)
                    cand_y.append(node.y)

            fig.add_trace(
                go.Scatter(
                    x=cand_x,
                    y=cand_y,
                    mode="lines",
                    line=dict(color="#D97706", width=2.5, dash="dot"),
                    opacity=0.65,
                    name=f"Alt: {label}",
                    hoverinfo="text",
                    hovertext=f"Candidate Route: {label}<br>{' → '.join(c_route)}",
                    showlegend=True,
                )
            )

    # 3. Selected Shortest Route (Bold Teal Line with Glow)
    if highlight_route and len(highlight_route) > 1:
        route_x: List[float] = []
        route_y: List[float] = []
        route_text: List[str] = []

        for step_idx, node_id in enumerate(highlight_route):
            node = network.get_node(node_id)
            if node:
                route_x.append(node.x)
                route_y.append(node.y)
                route_text.append(f"Waypoint {step_idx + 1}: {node.label} ({node.id})")

        # Glow layer
        fig.add_trace(
            go.Scatter(
                x=route_x,
                y=route_y,
                mode="lines",
                line=dict(color="#0F9D92", width=6.5),
                opacity=0.3,
                hoverinfo="none",
                showlegend=False,
            )
        )
        # Main route
        fig.add_trace(
            go.Scatter(
                x=route_x,
                y=route_y,
                mode="lines+markers",
                line=dict(color="#0F9D92", width=3.5),
                marker=dict(size=7, color="#0F9D92", symbol="circle"),
                hoverinfo="text",
                hovertext=route_text,
                name="Optimized Dijkstra Route",
                showlegend=True,
            )
        )

    # 4. Network Nodes by Type
    node_types = ["station", "hospital", "intersection"]
    for ntype in node_types:
        style = NODE_STYLE_MAP[ntype]
        matching_nodes = [n for n in network.nodes.values() if n.node_type == ntype]
        if not matching_nodes:
            continue

        nx = [n.x for n in matching_nodes]
        ny = [n.y for n in matching_nodes]
        n_text = []

        for n in matching_nodes:
            amb_info = ""
            if ambulances:
                here_ambs = [a for a in ambulances.values() if a.current_node == n.id]
                if here_ambs:
                    amb_str = ", ".join(f"{a.id} ({a.status})" for a in here_ambs)
                    amb_info = f"<br>Ambulances: <b>{amb_str}</b>"

            inc_info = ""
            if incidents:
                here_incs = [i for i in incidents.values() if i.location == n.id and i.status != "Completed"]
                if here_incs:
                    inc_str = ", ".join(f"{i.id} [{i.priority}]" for i in here_incs)
                    inc_info = f"<br>Incidents: <b>{inc_str}</b>"

            n_text.append(
                f"<b>{n.label}</b> ({n.id})<br>"
                f"Zone: {n.zone} &bull; Type: {style['name']}<br>"
                f"Degree: {network.get_node_degree(n.id)}"
                f"{amb_info}{inc_info}"
            )

        # Label visible for stations and hospitals
        labels = [n.label for n in matching_nodes] if ntype in ["station", "hospital"] else None

        fig.add_trace(
            go.Scatter(
                x=nx,
                y=ny,
                mode="markers+text" if labels else "markers",
                marker=dict(
                    size=style["size"],
                    color=style["color"],
                    symbol=style["symbol"],
                    line=dict(color="#FFFFFF", width=1.5),
                ),
                text=labels,
                textposition="top center",
                textfont=dict(size=9, color="#0F172A", family="sans-serif"),
                hoverinfo="text",
                hovertext=n_text,
                name=style["name"],
                showlegend=True,
            )
        )

    # 5. Active Pending Incidents (Prominent Red Diamonds)
    if incidents:
        pending_list = [i for i in incidents.values() if i.is_pending]
        if pending_list:
            inc_x = []
            inc_y = []
            inc_text = []
            for inc in pending_list:
                node = network.get_node(inc.location)
                if node:
                    inc_x.append(node.x)
                    inc_y.append(node.y)
                    inc_text.append(
                        f"<b>CALL: {inc.id}</b> [{inc.priority.upper()}]<br>"
                        f"Location: {node.label} ({node.id})<br>"
                        f"Details: {inc.description}<br>"
                        f"Reported: {inc.created_at}"
                    )

            fig.add_trace(
                go.Scatter(
                    x=inc_x,
                    y=inc_y,
                    mode="markers+text",
                    marker=dict(
                        size=18,
                        color="#DC2626",
                        symbol="diamond",
                        line=dict(color="#FFFFFF", width=2),
                    ),
                    text=[i.id for i in pending_list],
                    textposition="bottom center",
                    textfont=dict(size=10, color="#DC2626", family="sans-serif"),
                    hoverinfo="text",
                    hovertext=inc_text,
                    name="Pending Calls",
                    showlegend=True,
                )
            )

    # 6. Highlights for Source and Target
    if selected_source and network.get_node(selected_source):
        src_node = network.get_node(selected_source)
        fig.add_trace(
            go.Scatter(
                x=[src_node.x],
                y=[src_node.y],
                mode="markers",
                marker=dict(size=24, color="rgba(15, 157, 146, 0.35)", symbol="circle"),
                hoverinfo="none",
                showlegend=False,
            )
        )

    if selected_target and network.get_node(selected_target):
        dst_node = network.get_node(selected_target)
        fig.add_trace(
            go.Scatter(
                x=[dst_node.x],
                y=[dst_node.y],
                mode="markers",
                marker=dict(size=26, color="rgba(220, 38, 38, 0.35)", symbol="circle"),
                hoverinfo="none",
                showlegend=False,
            )
        )

    # Layout configuration
    layout_dict: Dict[str, Any] = dict(
        height=height,
        margin=dict(l=15, r=15, t=15, b=45),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        hovermode="closest",
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[min_x - pad_x, max_x + pad_x],
            fixedrange=True,
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[min_y - pad_y, max_y + pad_y],
            scaleanchor="x",
            scaleratio=1.0,
            fixedrange=True,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.14,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="#E2E8F0",
            borderwidth=1,
            font=dict(size=10, color="#1E293B"),
        ),
    )

    if title:
        layout_dict["title"] = dict(text=f"<b>{title}</b>", font=dict(size=13, color="#0F172A"), x=0.02, y=0.98)

    fig.update_layout(**layout_dict)
    return fig
