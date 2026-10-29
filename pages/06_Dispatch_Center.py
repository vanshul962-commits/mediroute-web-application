"""MediRoute — Intelligent Dispatch Center (Page 6).

Interactive dispatch optimization workspace. Evaluates vehicle candidates using
Dijkstra shortest paths, renders alternative routes, explains greedy rationale,
supports batch dispatch and strategy comparisons, and commits atomic dispatches.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd

from algorithms.greedy_dispatch import (
    greedy_batch_dispatch,
    nearest_available_dispatch,
    priority_aware_dispatch,
)
from simulation.state_manager import get_simulation_state
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


def main():
    st.set_page_config(page_title="MediRoute — Dispatch Center", page_icon="✚", layout="wide")
    apply_custom_styles()
    require_authentication()
    state = get_simulation_state()
    metrics = state.get_summary_metrics()

    render_command_bar(
        title="Dispatch Center",
        subtitle="Dijkstra Shortest Path Routing & Greedy Candidate Selection Workspace",
        show_dispatch_btn=False,
        simulation_step=metrics["simulation_step"],
    )

    # Top KPI Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Pending Calls", metrics["pending_incidents"], "Awaiting response", "#DC2626")
    with c2:
        render_kpi_card("Available Fleet", metrics["available_ambulances"], "Eligible candidates", "#16A34A")
    with c3:
        render_kpi_card("Critical Pending", metrics["critical_pending"], "Requires priority triage", "#B91C1C")
    with c4:
        render_kpi_card("Committed Dispatches", metrics["total_dispatches"], "Historical total", "#0D1B2A")

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    pending_incidents = [i for i in state.incidents.values() if i.is_pending]

    if not pending_incidents:
        st.markdown(
            """
            <div style="background-color: #FFFFFF; border: 1px dashed #CBD5E1; border-radius: 8px; padding: 2.5rem; text-align: center; color: #475569;">
                <h3 style="color: #0D1B2A; margin-top: 0;">All Calls Resolved</h3>
                <p>There are no emergency calls currently pending dispatch. Use <strong>Live Simulation</strong> to simulate an emergency surge, or <strong>Emergency Incidents</strong> to log a call.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_disclaimer()
        return

    # Operational Dispatch Tabs
    tab_single, tab_batch, tab_compare = st.tabs(
        ["Single Emergency Dispatch", "Multi-Incident Batch Dispatch (Strategy C)", "Strategy Comparison Matrix"]
    )

    # =========================================================================
    # TAB 1: Single Emergency Dispatch
    # =========================================================================
    with tab_single:
        # Determine initial selection if preselected from Overview
        preselected_id = st.session_state.get("selected_incident_id")
        pending_ids = [i.id for i in pending_incidents]
        default_idx = 0
        if preselected_id in pending_ids:
            default_idx = pending_ids.index(preselected_id)

        sel_col1, sel_col2 = st.columns([7, 5])
        with sel_col1:
            selected_inc_id = st.selectbox(
                "Select Emergency Incident to Dispatch:",
                options=pending_ids,
                index=default_idx,
                format_func=lambda iid: (
                    f"{iid} [{state.incidents[iid].priority.upper()}] — "
                    f"{state.incidents[iid].location} ({state.network.get_node(state.incidents[iid].location).label if state.network.get_node(state.incidents[iid].location) else ''})"
                ),
            )
            # Clear preselected once consumed
            if "selected_incident_id" in st.session_state:
                del st.session_state["selected_incident_id"]

        with sel_col2:
            selected_strategy = st.radio(
                "Optimization Strategy:",
                options=["Strategy A: Nearest Available Ambulance", "Strategy B: Priority-Aware Greedy"],
                horizontal=True,
            )

        target_incident = state.incidents[selected_inc_id]

        # Execute candidate evaluation via Dijkstra
        if "Strategy A" in selected_strategy:
            dispatch_result = nearest_available_dispatch(state.network, target_incident, state.ambulances)
        else:
            dispatch_result = priority_aware_dispatch(state.network, target_incident, state.ambulances)

        # Split Layout: Route Map (7 cols) | Decision Support Card (5 cols)
        map_col, info_col = st.columns([7, 5])

        with map_col:
            st.markdown(
                """
                <div class="mr-panel-header">
                    <div>
                        <span class="mr-panel-title">Optimal Route Trajectory & Competing Paths</span>
                        <div class="mr-panel-subtitle">Dijkstra Shortest Path (Teal) vs. Alternative Units (Dotted)</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            candidate_paths = []
            for cand in dispatch_result.candidates:
                if cand.eligible and cand.ambulance_id != dispatch_result.selected_ambulance_id:
                    candidate_paths.append((cand.path, f"{cand.ambulance_id} ({cand.travel_time:.1f}m)"))

            fig = build_network_figure(
                network=state.network,
                ambulances=state.ambulances,
                incidents=state.incidents,
                highlight_route=dispatch_result.route if dispatch_result.is_successful else None,
                candidate_routes=candidate_paths,
                selected_source=dispatch_result.route[0] if (dispatch_result.route and len(dispatch_result.route) > 0) else None,
                selected_target=target_incident.location,
                title=f"Shortest Path to {target_incident.location}",
                height=460,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})

        with info_col:
            st.markdown(
                """
                <div class="mr-panel-header">
                    <div>
                        <span class="mr-panel-title">Dispatch Recommendation</span>
                        <div class="mr-panel-subtitle">Algorithmic selection & simulated travel latency</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if dispatch_result.is_successful:
                st.markdown(
                    f"""
                    <div style="background-color: #EBF8F6; border: 1px solid #B8EBE2; border-radius: 8px; padding: 1rem 1.15rem; margin-bottom: 0.85rem;">
                        <div style="font-size: 0.72rem; font-weight: 700; color: #0F9D92; text-transform: uppercase; letter-spacing: 0.04em;">
                            RECOMMENDED AMBULANCE UNIT
                        </div>
                        <div style="font-size: 1.45rem; font-weight: 700; color: #0D1B2A; margin: 0.2rem 0;">
                            {dispatch_result.selected_ambulance_id} ({dispatch_result.selected_call_sign})
                        </div>
                        <div style="font-size: 0.95rem; color: #1E293B; font-weight: 600;">
                            Simulated Travel Time: <strong>{dispatch_result.estimated_travel_time:.1f} minutes</strong>
                        </div>
                        <div style="font-size: 0.8rem; color: #64748B; margin-top: 0.35rem;">
                            Route: <code>{' › '.join(dispatch_result.route)}</code> ({len(dispatch_result.route)} nodes)
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                    <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 6px; padding: 0.85rem; margin-bottom: 0.85rem;">
                        <div style="font-size: 0.78rem; font-weight: 700; color: #0D1B2A; margin-bottom: 0.25rem;">
                            Decision Rationale:
                        </div>
                        <div style="font-size: 0.82rem; color: #475569; line-height: 1.45;">
                            {dispatch_result.explanation}
                        </div>
                        <div style="font-size: 0.75rem; color: #64748B; margin-top: 0.45rem; border-top: 1px solid #F1F5F9; padding-top: 0.35rem;">
                            Explored Vertices: <strong>{dispatch_result.explored_nodes_total}</strong> &bull;
                            Solve Time: <strong>{dispatch_result.computation_time_ms:.4f} ms</strong>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if st.button("Confirm & Dispatch Ambulance Now", type="primary", use_container_width=True):
                    ok, msg = state.commit_dispatch(
                        incident_id=target_incident.id,
                        ambulance_id=dispatch_result.selected_ambulance_id,
                        strategy=dispatch_result.strategy,
                        route=dispatch_result.route,
                        travel_time=dispatch_result.estimated_travel_time or 0.0,
                        computation_time_ms=dispatch_result.computation_time_ms,
                    )
                    if ok:
                        st.success(f"Dispatched: {msg}")
                        st.rerun()
                    else:
                        st.error(msg)
            else:
                st.error(f"Dispatch Unavailable: {dispatch_result.status}")
                st.warning(dispatch_result.explanation)

        # Candidate Comparison Table
        st.markdown(
            """
            <div class="mr-panel-header" style="margin-top: 1rem;">
                <div>
                    <span class="mr-panel-title">Evaluated Candidate Vehicles (Dijkstra Profiling)</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        cand_rows = []
        for c in dispatch_result.candidates:
            cand_rows.append(
                {
                    "Rank": c.rank if c.rank else "—",
                    "Ambulance ID": c.ambulance_id,
                    "Call Sign": c.call_sign,
                    "Location": c.current_node,
                    "Status": c.status,
                    "Capability": c.capability,
                    "Eligibility": "Eligible" if c.eligible else f"Ineligible ({c.ineligibility_reason})",
                    "Simulated Travel": f"{c.travel_time:.1f} min" if c.travel_time != float("inf") else "—",
                    "Explored Nodes": c.explored_nodes,
                    "Dijkstra Time (ms)": f"{c.dijkstra_time_ms:.4f}",
                }
            )
        st.dataframe(pd.DataFrame(cand_rows), hide_index=True, use_container_width=True)

    # =========================================================================
    # TAB 2: Multi-Incident Batch Dispatch (Strategy C)
    # =========================================================================
    with tab_batch:
        st.markdown(
            """
            <div class="mr-panel-header">
                <div>
                    <span class="mr-panel-title">Greedy Batch Multi-Incident Dispatch</span>
                    <div class="mr-panel-subtitle">Sequential Priority-Ordered Allocation (Critical > High > Med > Low)</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write(f"Evaluating all **{len(pending_incidents)} pending incidents** simultaneously against currently available fleet.")

        batch_result = greedy_batch_dispatch(state.network, pending_incidents, state.ambulances)

        bc1, bc2, bc3, bc4 = st.columns(4)
        with bc1:
            render_kpi_card("Planned Assignments", len(batch_result.assignments), "Allocated in batch", "#16A34A")
        with bc2:
            render_kpi_card("Unassigned Calls", len(batch_result.unassigned_incidents), "Exhausted / unreachable", "#DC2626")
        with bc3:
            render_kpi_card("Cumulative Travel", f"{batch_result.total_travel_time:.1f}m", "Total simulated minutes", "#0F9D92")
        with bc4:
            render_kpi_card("Batch Solve Time", f"{batch_result.total_computation_time_ms:.3f}ms", "Total CPU runtime", "#0D1B2A")

        if batch_result.assignments:
            st.markdown("<strong>Planned Batch Assignments:</strong>", unsafe_allow_html=True)
            batch_rows = []
            for a in batch_result.assignments:
                batch_rows.append(
                    {
                        "Incident ID": a.incident_id,
                        "Priority": a.incident_priority,
                        "Location": a.incident_location,
                        "Assigned Unit": a.selected_ambulance_id,
                        "Call Sign": a.selected_call_sign,
                        "Simulated Travel": f"{a.estimated_travel_time:.1f} min",
                        "Route": " › ".join(a.route),
                    }
                )
            st.dataframe(pd.DataFrame(batch_rows), hide_index=True, use_container_width=True)

            if st.button("Commit Entire Batch Dispatch", type="primary", use_container_width=True):
                success_count = 0
                for a in batch_result.assignments:
                    ok, _ = state.commit_dispatch(
                        incident_id=a.incident_id,
                        ambulance_id=a.selected_ambulance_id,
                        strategy=a.strategy,
                        route=a.route,
                        travel_time=a.estimated_travel_time or 0.0,
                        computation_time_ms=a.computation_time_ms,
                    )
                    if ok:
                        success_count += 1
                st.success(f"Committed {success_count} batch assignments.")
                st.rerun()

    # =========================================================================
    # TAB 3: Strategy Comparison Matrix
    # =========================================================================
    with tab_compare:
        st.markdown(
            """
            <div class="mr-panel-header">
                <div>
                    <span class="mr-panel-title">Side-by-Side Strategy Evaluation</span>
                    <div class="mr-panel-subtitle">Evaluated on the exact same snapshot without state mutation</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        cmp_inc_id = st.selectbox(
            "Select Incident for Comparative Audit:",
            options=pending_ids,
            key="cmp_inc_select",
            format_func=lambda iid: f"{iid} [{state.incidents[iid].priority}] at {state.incidents[iid].location}",
        )
        cmp_inc = state.incidents[cmp_inc_id]

        res_a = nearest_available_dispatch(state.network, cmp_inc, state.ambulances)
        res_b = priority_aware_dispatch(state.network, cmp_inc, state.ambulances)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(
                f"""
                <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-top: 3px solid #0F9D92; border-radius: 6px; padding: 1rem;">
                    <h4 style="color: #0F9D92; margin-top: 0;">Strategy A: Nearest Available</h4>
                    <p style="font-size: 0.8rem; color: #64748B;">Optimizes strictly for minimal travel time, ignoring medical equipment tiers.</p>
                    <ul style="font-size: 0.85rem; line-height: 1.6; padding-left: 1.2rem;">
                        <li><strong>Selected Unit:</strong> {res_a.selected_ambulance_id or 'None'}</li>
                        <li><strong>Simulated Travel:</strong> {res_a.estimated_travel_time or 0.0:.1f} min</li>
                        <li><strong>Route:</strong> {' › '.join(res_a.route) if res_a.route else 'N/A'}</li>
                        <li><strong>Solve Time:</strong> {res_a.computation_time_ms:.4f} ms</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_b:
            st.markdown(
                f"""
                <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-top: 3px solid #D97706; border-radius: 6px; padding: 1rem;">
                    <h4 style="color: #D97706; margin-top: 0;">Strategy B: Priority-Aware</h4>
                    <p style="font-size: 0.8rem; color: #64748B;">Prioritizes Advanced Life Support (ALS) for Critical calls, then travel time.</p>
                    <ul style="font-size: 0.85rem; line-height: 1.6; padding-left: 1.2rem;">
                        <li><strong>Selected Unit:</strong> {res_b.selected_ambulance_id or 'None'}</li>
                        <li><strong>Simulated Travel:</strong> {res_b.estimated_travel_time or 0.0:.1f} min</li>
                        <li><strong>Route:</strong> {' › '.join(res_b.route) if res_b.route else 'N/A'}</li>
                        <li><strong>Solve Time:</strong> {res_b.computation_time_ms:.4f} ms</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

    render_disclaimer()


if __name__ == "__main__":
    main()
