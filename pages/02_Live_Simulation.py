"""MediRoute — Live Simulation (Page 2).

Interactive simulation step controller, emergency surge generator, and active mission tracking.
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


def main():
    st.set_page_config(page_title="MediRoute — Live Simulation", page_icon="✚", layout="wide")
    apply_custom_styles()
    require_authentication()
    state = get_simulation_state()
    metrics = state.get_summary_metrics()

    render_command_bar(
        title="Live Simulation",
        subtitle="Time-Step Execution & Dynamic Incident Lifecycle Progression",
        show_dispatch_btn=True,
        simulation_step=metrics["simulation_step"],
    )

    # Telemetry metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_kpi_card("Clock Time-Step", f"#{metrics['simulation_step']}", "Logical clock ticks", "#0D1B2A")
    with m2:
        render_kpi_card("Available Fleet", f"{metrics['available_ambulances']} / {metrics['total_ambulances']}", "Ready to deploy", "#16A34A")
    with m3:
        render_kpi_card("Units En Route", metrics["busy_ambulances"], "Responding to incidents", "#DC2626")
    with m4:
        render_kpi_card("Pending Emergencies", metrics["pending_incidents"], f"{metrics['critical_pending']} critical priority", "#D97706")

    # Command Toolbar
    st.markdown(
        """
        <div class="mr-panel-header">
            <div>
                <span class="mr-panel-title">Simulation Step Controls</span>
                <div class="mr-panel-subtitle">Advance time intervals or trigger synthetic load surges</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        if st.button("Advance Step (+1)", use_container_width=True):
            res_msg = advance_simulation_step(state)
            st.toast(res_msg, icon="⏩")
            st.rerun()
    with b2:
        if st.button("Simulate Emergency Surge (+2 Calls)", use_container_width=True):
            new_calls = trigger_emergency_surge(state, count=2)
            st.toast(f"Generated {len(new_calls)} new synthetic incidents.", icon="🚨")
            st.rerun()
    with b3:
        if st.button("Recall Fleet to Stations", use_container_width=True):
            count = return_all_ambulances_home(state)
            st.toast(f"Recalled {count} vehicles to stations.", icon="🔄")
            st.rerun()
    with b4:
        if st.button("Reset Simulation State", use_container_width=True):
            reset_global_simulation()
            st.toast("Simulation state restored to default.")
            st.rerun()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Active Dispatches Resolution Section
    assigned_incidents = [inc for inc in state.incidents.values() if inc.status == "Assigned"]
    if assigned_incidents:
        st.markdown(
            f"""
            <div class="mr-panel-header">
                <div>
                    <span class="mr-panel-title">Active Dispatches in Progress ({len(assigned_incidents)})</span>
                    <div class="mr-panel-subtitle">En route units progressing toward scene</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for inc in assigned_incidents:
            col_info, col_act = st.columns([9, 3])
            with col_info:
                st.markdown(
                    f"""
                    <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 6px; padding: 0.75rem 1rem; margin-bottom: 0.5rem; font-size: 0.85rem;">
                        <strong>{inc.id}</strong> [{inc.priority.upper()}] &bull; Responding Vehicle: <strong>{inc.assigned_ambulance_id}</strong> &bull;
                        Target: <strong>{inc.location}</strong> &bull; Simulated Travel: <strong>{inc.simulated_travel_time:.1f} min</strong>
                        <div style="font-size: 0.78rem; color: #64748B; margin-top: 0.2rem;">
                            Route: {' › '.join(inc.route) if inc.route else 'Direct'}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_act:
                if st.button(f"Resolve Mission ({inc.id})", key=f"comp_{inc.id}", use_container_width=True):
                    ok, msg = state.complete_mission(inc.id, return_to_hospital=True)
                    if ok:
                        st.toast(msg, icon="✓")
                        st.rerun()
                    else:
                        st.error(msg)

    # Real-Time Road Topology Map
    st.markdown(
        """
        <div class="mr-panel-header" style="margin-top: 1rem;">
            <div>
                <span class="mr-panel-title">Live Topological Network & Unit Tracking</span>
                <div class="mr-panel-subtitle">Displaying fixed node coordinates and live simulated fleet positions</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    fig = build_network_figure(
        network=state.network,
        ambulances=state.ambulances,
        incidents=state.incidents,
        title="Simulated Fleet Positions & Road Network",
        height=460,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})

    render_disclaimer()


if __name__ == "__main__":
    main()
