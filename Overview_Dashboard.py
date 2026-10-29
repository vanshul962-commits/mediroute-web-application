"""MediRoute — Emergency Vehicle Dispatch Optimizer.

Main Application Entry Point and Executive Overview Dashboard.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd

from simulation.state_manager import get_simulation_state, reset_global_simulation
from simulation.simulator import (
    advance_simulation_step,
    dispatch_history_to_dataframe,
    return_all_ambulances_home,
    trigger_emergency_surge,
)
from ui.auth import require_authentication
from ui.components import (
    render_command_bar,
    render_disclaimer,
    render_kpi_card,
    render_priority_badge,
    render_status_badge,
)
from ui.styles import apply_custom_styles
from visualization.network_graph import build_network_figure
from visualization.performance import build_benchmark_runtime_chart, run_dijkstra_scalability_benchmark


def main():
    st.set_page_config(
        page_title="MediRoute — Overview Dashboard",
        page_icon="✚",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    apply_custom_styles()
    require_authentication()
    state = get_simulation_state()
    metrics = state.get_summary_metrics()

    # 1. Top Enterprise Command Bar
    render_command_bar(
        title="Overview Dashboard",
        subtitle="Emergency Fleet & Dispatch Operations",
        show_dispatch_btn=True,
        simulation_step=metrics["simulation_step"],
    )

    # 2. Restrained Secondary Simulation Controls Bar
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([3, 3, 3, 3])
    with ctrl_col1:
        if st.button("Advance Step (+1)", use_container_width=True):
            msg = advance_simulation_step(state)
            st.toast(msg, icon="⏩")
            st.rerun()
    with ctrl_col2:
        if st.button("Simulate Emergency (+2 Calls)", use_container_width=True):
            new_calls = trigger_emergency_surge(state, count=2)
            st.toast(f"Surge logged {len(new_calls)} new calls.", icon="🚨")
            st.rerun()
    with ctrl_col3:
        if st.button("Recall Fleet to Stations", use_container_width=True):
            c = return_all_ambulances_home(state)
            st.toast(f"Returned {c} units to base stations.", icon="🔄")
            st.rerun()
    with ctrl_col4:
        with st.popover("Settings & Reset ⚙️", use_container_width=True):
            st.markdown("<strong>Simulation Parameters</strong>", unsafe_allow_html=True)
            st.caption(f"Network: {state.network.name}")
            st.caption(f"Vertices: {len(state.network.nodes)} | Edges: {len(state.network.edges)}")
            st.divider()
            if st.button("Reset Simulation Snapshot", use_container_width=True):
                reset_global_simulation()
                st.toast("Simulation state restored to baseline snapshot.")
                st.rerun()

    # 3. Responsive SaaS KPI Metric Cards (5 Cards across)
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        render_kpi_card(
            title="Total Fleet",
            value=metrics["total_ambulances"],
            subtext="Registered units",
            pill_text="Active",
            pill_type="blue",
            icon_symbol="🚑",
            icon_bg="#EFF6FF",
            icon_color="#1D4ED8",
        )
    with k2:
        render_kpi_card(
            title="Available Units",
            value=metrics["available_ambulances"],
            subtext="Ready to deploy",
            pill_text="Ready",
            pill_type="green",
            icon_symbol="✓",
            icon_bg="#DCFCE7",
            icon_color="#15803D",
        )
    with k3:
        render_kpi_card(
            title="Units En Route",
            value=metrics["busy_ambulances"],
            subtext="Active responses",
            pill_text="Busy",
            pill_type="red",
            icon_symbol="›",
            icon_bg="#FEE2E2",
            icon_color="#DC2626",
        )
    with k4:
        render_kpi_card(
            title="Pending Calls",
            value=metrics["pending_incidents"],
            subtext=f"{metrics['critical_pending']} critical priority",
            pill_text="Queue",
            pill_type="amber",
            icon_symbol="!",
            icon_bg="#FEF3C7",
            icon_color="#D97706",
        )
    with k5:
        render_kpi_card(
            title="Completed Runs",
            value=metrics["completed_incidents"],
            subtext=f"Avg {metrics['average_response_time']}m travel",
            pill_text="Resolved",
            pill_type="green",
            icon_symbol="🏁",
            icon_bg="#EBF8F6",
            icon_color="#0F9D92",
        )

    # 4. Main Balanced Operations Deck (7 : 5 Desktop Ratio)
    map_col, incident_col = st.columns([7, 5])

    # LEFT COLUMN: Fully Scaled Road Network Map
    with map_col:
        st.markdown(
            """
            <div class="mr-panel-top">
                <div>
                    <span class="mr-panel-heading">Metropolitan Road Network & Fleet Telemetry</span>
                    <div class="mr-panel-caption">Interactive 20-Node Topology &bull; Station Bases, Hospitals, & Units</div>
                </div>
                <div>
                    <span class="mr-pill-badge mr-pill-blue">20 Vertices | 37 Edges</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        fig = build_network_figure(
            network=state.network,
            ambulances=state.ambulances,
            incidents=state.incidents,
            height=460,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})

        # Compact Network Telemetry Summary
        st.markdown(
            f"""
            <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.6rem 0.9rem; font-size: 0.76rem; color: #475569; display: flex; justify-content: space-between; flex-wrap: wrap; margin-top: 0.2rem;">
                <span><strong>Topology:</strong> 20 Vertices &bull; 37 Edges</span>
                <span><strong>Bases:</strong> 3 Stations (Alpha, Beta, Gamma)</span>
                <span><strong>Receiving:</strong> 3 Hospitals</span>
                <span><strong>Shortest-Path:</strong> Dijkstra SSSP</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # RIGHT COLUMN: Prioritized Pending Incident Queue
    with incident_col:
        st.markdown(
            f"""
            <div class="mr-panel-top">
                <div>
                    <span class="mr-panel-heading">Active Incident Queue</span>
                    <div class="mr-panel-caption">Priority-Ranked Pending Calls Awaiting Vehicle Dispatch</div>
                </div>
                <div>
                    <span class="mr-badge mr-badge-critical">{metrics['pending_incidents']} PENDING</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        pending_list = [i for i in state.incidents.values() if i.is_pending]
        pending_list.sort(key=lambda i: (i.priority_rank, i.id))

        if not pending_list:
            st.markdown(
                """
                <div style="background-color: #FFFFFF; border: 1px dashed #CBD5E1; border-radius: 8px; padding: 2.5rem 1rem; text-align: center; color: #64748B;">
                    <div style="font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 0.25rem;">All Clear — Queue Empty</div>
                    <div style="font-size: 0.8rem;">All emergency calls have been assigned or completed. Use the controls above to trigger synthetic incident reports.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for inc in pending_list[:3]:
                loc_node = state.network.get_node(inc.location)
                loc_name = loc_node.label if loc_node else inc.location

                card_col_info, card_col_btn = st.columns([8, 4])

                with card_col_info:
                    st.markdown(
                        f"""
                        <div class="mr-incident-item">
                            <div class="mr-incident-meta">
                                <span class="mr-incident-code">{inc.id}</span>
                                {render_priority_badge(inc.priority)}
                            </div>
                            <div class="mr-incident-place">
                                <strong>Location:</strong> {loc_name} (<code>{inc.location}</code>)
                            </div>
                            <div class="mr-incident-narrative">
                                {inc.description}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with card_col_btn:
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    if st.button("Dispatch ›", key=f"btn_disp_{inc.id}", type="primary", use_container_width=True):
                        st.session_state["selected_incident_id"] = inc.id
                        try:
                            st.switch_page("pages/06_Dispatch_Center.py")
                        except Exception:
                            st.info(f"Selected {inc.id}. Open Dispatch Center from sidebar.")

            if len(pending_list) > 3:
                st.caption(f"⚡ +{len(pending_list) - 3} additional calls in queue. Access all in Dispatch Center.")

            if st.button("Open Full Dispatch Center Queue ›", type="primary", key="btn_open_disp_queue", use_container_width=True):
                try:
                    st.switch_page("pages/06_Dispatch_Center.py")
                except Exception:
                    pass

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # 5. Lower Operational Deck: Recent Activity (5) | Performance (4) | Readiness (3)
    hist_col, chart_col, fleet_col = st.columns([5, 4, 3])

    with hist_col:
        st.markdown(
            """
            <div class="mr-panel-top">
                <div>
                    <span class="mr-panel-heading">Recent Dispatch Log</span>
                    <div class="mr-panel-caption">Audit Trail of Committed Ambulance Assignments</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if state.dispatch_history:
            df_hist = dispatch_history_to_dataframe(state)
            st.dataframe(
                df_hist[["timestamp", "incident_id", "ambulance_id", "strategy", "simulated_travel_time"]].tail(5),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("No dispatch records logged yet.")

    with chart_col:
        st.markdown(
            """
            <div class="mr-panel-top">
                <div>
                    <span class="mr-panel-heading">Algorithm Scalability Profile</span>
                    <div class="mr-panel-caption">Empirical Dijkstra Runtime vs. Graph Vertices |V|</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if "bench_df" not in st.session_state:
            st.session_state["bench_df"] = run_dijkstra_scalability_benchmark([10, 20, 35, 50], repeats=2)
        fig_bench = build_benchmark_runtime_chart(st.session_state["bench_df"])
        fig_bench.update_layout(height=210, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_bench, use_container_width=True)

    with fleet_col:
        st.markdown(
            """
            <div class="mr-panel-top">
                <div>
                    <span class="mr-panel-heading">Fleet Base Telemetry</span>
                    <div class="mr-panel-caption">Station Allocation Readiness</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for amb in list(state.ambulances.values())[:4]:
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.35rem 0; border-bottom: 1px solid #F1F5F9; font-size: 0.8rem;">
                    <div>
                        <strong>{amb.id}</strong> ({amb.call_sign})
                        <div style="font-size: 0.72rem; color: #64748B;">{amb.capability} &bull; Base: {amb.home_station}</div>
                    </div>
                    {render_status_badge(amb.status)}
                </div>
                """,
                unsafe_allow_html=True,
            )

    # 6. Compact Educational Disclaimer Footer
    render_disclaimer()


if __name__ == "__main__":
    main()
