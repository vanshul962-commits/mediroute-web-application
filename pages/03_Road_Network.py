"""MediRoute — Road Network Management & Graph Inspector (Page 3).

Topological graph analysis, adjacency list inspection, node degree profiling,
and road travel-time validation.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd

from graph.sample_network import build_default_metro_network, build_disconnected_network, generate_random_network
from simulation.state_manager import get_simulation_state
from ui.auth import require_authentication
from ui.components import render_command_bar, render_disclaimer, render_kpi_card
from ui.styles import apply_custom_styles
from visualization.network_graph import build_network_figure


def main():
    st.set_page_config(page_title="MediRoute — Road Network", page_icon="✚", layout="wide")
    apply_custom_styles()
    require_authentication()
    state = get_simulation_state()
    net = state.network
    metrics = state.get_summary_metrics()

    render_command_bar(
        title="Road Network",
        subtitle="Graph Topology, Adjacency List Structure, & Edge Weights",
        show_dispatch_btn=True,
        simulation_step=metrics["simulation_step"],
    )

    # Graph KPI summary
    total_nodes = len(net.nodes)
    total_edges = len(net.edges)
    stations_count = len(net.stations())
    hospitals_count = len(net.hospitals())
    intersections_count = len(net.intersections())

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        render_kpi_card("Graph Vertices |V|", total_nodes, "Intersections & bases", "#0D1B2A")
    with m2:
        render_kpi_card("Graph Edges |E|", total_edges, "Traversable segments", "#0F9D92")
    with m3:
        render_kpi_card("Stations", stations_count, "Ambulance bases", "#16A34A")
    with m4:
        render_kpi_card("Hospitals", hospitals_count, "Receiving trauma centers", "#0D1B2A")
    with m5:
        render_kpi_card("Intersections", intersections_count, "Urban transit junctions", "#64748B")

    # Topology Controls Expander
    with st.expander("Topology Configurations & Generators", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("<strong>Baseline Grid</strong>", unsafe_allow_html=True)
            st.caption("Restores the standard 20-node Metro Central emergency network.")
            if st.button("Restore Default Network", use_container_width=True):
                state.network = build_default_metro_network()
                st.toast("Restored 20-node Metro network.")
                st.rerun()

        with c2:
            st.markdown("<strong>Procedural Graph Generator</strong>", unsafe_allow_html=True)
            seed_val = st.number_input("Seed", min_value=1, max_value=9999, value=42)
            node_cnt = st.slider("Node Count |V|", min_value=10, max_value=40, value=20)
            if st.button("Generate Seeded Graph", use_container_width=True):
                state.network = generate_random_network(seed=int(seed_val), num_nodes=int(node_cnt))
                st.toast(f"Generated network with {node_cnt} vertices.")
                st.rerun()

        with c3:
            st.markdown("<strong>Disconnected Topology Test</strong>", unsafe_allow_html=True)
            st.caption("Creates two isolated mainland/island components to test unreachable paths.")
            if st.button("Load Disconnected Graph", use_container_width=True):
                state.network = build_disconnected_network()
                st.toast("Loaded disconnected components.")
                st.rerun()

    # Network Visualization & Node Inspector side-by-side
    map_col, inspect_col = st.columns([7, 5])

    with map_col:
        st.markdown(
            """
            <div class="mr-panel-header">
                <div>
                    <span class="mr-panel-title">Topological Road Graph</span>
                    <div class="mr-panel-subtitle">Weighted Road Segments & Strategic Base Stations</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        fig = build_network_figure(
            network=state.network,
            ambulances=state.ambulances,
            incidents=state.incidents,
            title="Road Graph Topology",
            height=460,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})

    with inspect_col:
        st.markdown(
            """
            <div class="mr-panel-header">
                <div>
                    <span class="mr-panel-title">Adjacency List & Vertex Inspector</span>
                    <div class="mr-panel-subtitle">Inspect outgoing road segments and travel latencies</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        node_keys = state.network.node_ids()
        selected_node = st.selectbox(
            "Select Vertex to Inspect:",
            options=node_keys,
            format_func=lambda nid: f"{nid} — {state.network.get_node(nid).label}",
        )

        if selected_node:
            node_obj = state.network.get_node(selected_node)
            neighbors = state.network.get_neighbors(selected_node)

            st.markdown(
                f"""
                <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 6px; padding: 0.85rem; margin-bottom: 0.75rem;">
                    <div style="font-size: 1rem; font-weight: 700; color: #0D1B2A;">{node_obj.label}</div>
                    <div style="font-size: 0.8rem; color: #64748B; margin-top: 0.15rem;">
                        Node ID: <code>{node_obj.id}</code> &bull; Type: <strong>{node_obj.node_type.upper()}</strong> &bull; Zone: {node_obj.zone}
                    </div>
                    <div style="font-size: 0.8rem; color: #0F9D92; margin-top: 0.15rem;">
                        Coordinates: ({node_obj.x}, {node_obj.y}) &bull; Outgoing Degree: <strong>{len(neighbors)}</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if neighbors:
                nbr_records = []
                for nbr in neighbors:
                    target_obj = state.network.get_node(nbr["to"])
                    nbr_records.append(
                        {
                            "Neighbor": f"{nbr['to']} ({target_obj.label if target_obj else ''})",
                            "Simulated Travel": f"{nbr['travel_time']:.1f} min",
                            "Distance": f"{nbr['distance_km']:.1f} km",
                            "Road Name": nbr["road_name"],
                        }
                    )
                st.dataframe(pd.DataFrame(nbr_records), hide_index=True, use_container_width=True)
            else:
                st.warning("Vertex has zero outgoing road segments.")

        # Edge Weight Modifier
        with st.expander("Modify Road Segment Weight", expanded=False):
            if state.network.edges:
                edge_labels = [f"{e.u} <-> {e.v} ({e.road_name})" for e in state.network.edges]
                chosen_edge_idx = st.selectbox("Select Segment:", range(len(edge_labels)), format_func=lambda i: edge_labels[i])
                target_edge = state.network.edges[chosen_edge_idx]

                new_travel_time = st.number_input(
                    "Simulated Travel Time (min)",
                    min_value=0.5,
                    max_value=60.0,
                    value=float(target_edge.travel_time),
                    step=0.5,
                )

                if st.button("Apply Weight Update", type="primary"):
                    target_edge.travel_time = round(new_travel_time, 2)
                    for edge_entry in state.network.adjacency.get(target_edge.u, []):
                        if edge_entry["to"] == target_edge.v:
                            edge_entry["travel_time"] = round(new_travel_time, 2)
                    if target_edge.bidirectional:
                        for edge_entry in state.network.adjacency.get(target_edge.v, []):
                            if edge_entry["to"] == target_edge.u:
                                edge_entry["travel_time"] = round(new_travel_time, 2)
                    st.success(f"Updated '{target_edge.road_name}' travel time to {new_travel_time:.1f} min.")
                    st.rerun()

    render_disclaimer()


if __name__ == "__main__":
    main()
