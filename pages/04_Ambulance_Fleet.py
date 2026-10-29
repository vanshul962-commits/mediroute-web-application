"""MediRoute — Ambulance Fleet Management (Page 4).

Fleet monitoring, status filtering, vehicle capabilities, and operational lifecycle controls.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd

from simulation.simulator import fleet_to_dataframe
from simulation.state_manager import get_simulation_state
from ui.auth import require_authentication
from ui.components import (
    render_command_bar,
    render_disclaimer,
    render_kpi_card,
    render_status_badge,
)
from ui.styles import apply_custom_styles


def main():
    st.set_page_config(page_title="MediRoute — Ambulance Fleet", page_icon="✚", layout="wide")
    apply_custom_styles()
    require_authentication()
    state = get_simulation_state()
    fleet = state.ambulances
    metrics = state.get_summary_metrics()

    render_command_bar(
        title="Ambulance Fleet",
        subtitle="Vehicle Readiness, Life Support Capabilities, & Operational Assignments",
        show_dispatch_btn=True,
        simulation_step=metrics["simulation_step"],
    )

    # Summary metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Total Registered Units", metrics["total_ambulances"], "Active emergency fleet", "#0D1B2A")
    with c2:
        render_kpi_card("Available Units", metrics["available_ambulances"], "Immediate response ready", "#16A34A")
    with c3:
        render_kpi_card("Units En Route", metrics["busy_ambulances"], "Responding to incidents", "#DC2626")
    with c4:
        render_kpi_card("Out of Service", metrics["maintenance_ambulances"], "Maintenance / repair", "#64748B")

    # Filters Toolbar
    st.markdown(
        """
        <div class="mr-panel-header">
            <div>
                <span class="mr-panel-title">Fleet Telemetry & Filter Controls</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    f1, f2, f3 = st.columns(3)
    with f1:
        status_filter = st.selectbox("Status Filter", ["All", "Available", "Busy", "Maintenance"])
    with f2:
        capability_filter = st.selectbox("Capability Filter", ["All", "ALS (Advanced Life Support)", "BLS (Basic Life Support)"])
    with f3:
        search_kw = st.text_input("Search ID / Call Sign", placeholder="e.g. AMB-01")

    # Filter fleet
    filtered_ambs = list(fleet.values())
    if status_filter != "All":
        filtered_ambs = [a for a in filtered_ambs if a.status == status_filter]
    if capability_filter != "All":
        cap_val = "ALS" if "ALS" in capability_filter else "BLS"
        filtered_ambs = [a for a in filtered_ambs if a.capability == cap_val]
    if search_kw.strip():
        kw = search_kw.strip().lower()
        filtered_ambs = [a for a in filtered_ambs if kw in a.id.lower() or kw in a.call_sign.lower()]

    tab_cards, tab_table = st.tabs(["Vehicle Cards", "Fleet Telemetry Table"])

    with tab_cards:
        if not filtered_ambs:
            st.info("No vehicles match the selected filter criteria.")
        else:
            cols = st.columns(3)
            for idx, amb in enumerate(filtered_ambs):
                with cols[idx % 3]:
                    cap_color = "#1D4ED8" if amb.capability == "ALS" else "#475569"
                    st.markdown(
                        f"""
                        <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; padding: 1rem 1.15rem; margin-bottom: 0.85rem; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                                <strong style="font-size: 1rem; color: #0D1B2A;">{amb.id}</strong>
                                {render_status_badge(amb.status)}
                            </div>
                            <div style="font-size: 0.9rem; font-weight: 600; color: #1E293B; margin-bottom: 0.4rem;">
                                {amb.call_sign}
                            </div>
                            <div style="font-size: 0.8rem; color: #64748B; line-height: 1.55;">
                                Base Station: <strong>{amb.home_station}</strong><br>
                                Current Node: <strong>{amb.current_node}</strong><br>
                                Medical Tier: <span style="font-weight: 600; color: {cap_color};">{amb.capability}</span><br>
                                Completed Runs: <strong>{amb.assignments_completed}</strong><br>
                                Active Call: <strong>{amb.current_assigned_incident or 'None'}</strong><br>
                                Cumulative Response: <strong>{amb.total_travel_time_simulated:.1f} min</strong>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    act_col1, act_col2 = st.columns(2)
                    with act_col1:
                        if amb.status == "Available":
                            if st.button("Set Maintenance", key=f"maint_{amb.id}", use_container_width=True):
                                amb.status = "Maintenance"
                                st.rerun()
                        elif amb.status == "Maintenance":
                            if st.button("Set Available", key=f"avail_{amb.id}", use_container_width=True):
                                amb.status = "Available"
                                st.rerun()
                        elif amb.status == "Busy":
                            if st.button("Release Unit", key=f"rel_{amb.id}", use_container_width=True):
                                amb.complete()
                                st.rerun()
                    with act_col2:
                        if st.button("Recall Base", key=f"ret_{amb.id}", use_container_width=True):
                            amb.return_to_station()
                            st.rerun()

    with tab_table:
        df_fleet = fleet_to_dataframe(state)
        st.dataframe(df_fleet, hide_index=True, use_container_width=True)

    render_disclaimer()


if __name__ == "__main__":
    main()
