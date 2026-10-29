"""MediRoute — Emergency Incident Management (Page 5).

Synthetic emergency incident intake, priority classification, and triage queue management.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd

from simulation.incidents import PRIORITY_ORDER, validate_incident_input
from simulation.simulator import incidents_to_dataframe
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


def main():
    st.set_page_config(page_title="MediRoute — Emergency Incidents", page_icon="✚", layout="wide")
    apply_custom_styles()
    require_authentication()
    state = get_simulation_state()
    incidents = state.incidents
    metrics = state.get_summary_metrics()

    render_command_bar(
        title="Emergency Incidents",
        subtitle="Synthetic Call Intake, Priority Classification, & Triage Queues",
        show_dispatch_btn=True,
        simulation_step=metrics["simulation_step"],
    )

    # Incident metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Pending Emergencies", metrics["pending_incidents"], "Awaiting ambulance dispatch", "#DC2626")
    with c2:
        render_kpi_card("Dispatched Calls", metrics["assigned_incidents"], "Units en route to scene", "#0F9D92")
    with c3:
        render_kpi_card("Resolved Missions", metrics["completed_incidents"], "Successfully transported", "#16A34A")
    with c4:
        render_kpi_card("Critical Priority", metrics["critical_pending"], "Requires ALS cardiac triage", "#B91C1C")

    # Form to Log a New Synthetic Incident
    with st.expander("Log New Emergency Call", expanded=True):
        st.caption("Enter synthetic emergency report parameters. Data is simulated for DAA routing demonstration.")

        with st.form("new_incident_form"):
            col_loc, col_prio = st.columns(2)

            with col_loc:
                node_keys = state.network.node_ids()
                selected_loc = st.selectbox(
                    "Incident Location (Node):",
                    options=node_keys,
                    format_func=lambda nid: f"{nid} — {state.network.get_node(nid).label}",
                )

            with col_prio:
                selected_priority = st.selectbox(
                    "Urgency Priority Tier:",
                    options=list(PRIORITY_ORDER.keys()),
                    help="Critical: ALS Resuscitation; High: Immediate Response; Medium: Standard Urgent; Low: Non-Emergency",
                )

            desc_text = st.text_input(
                "Incident Description",
                placeholder="e.g. Simulated pedestrian collision with moderate roadway obstruction",
            )

            submitted = st.form_submit_button("Submit Emergency Call to Queue", type="primary", use_container_width=True)

            if submitted:
                is_valid, err_msg = validate_incident_input(
                    location=selected_loc,
                    priority=selected_priority,
                    description=desc_text,
                    valid_nodes=node_keys,
                )

                if not is_valid:
                    st.error(f"Validation Error: {err_msg}")
                else:
                    success, msg, new_inc = state.add_new_incident(
                        location=selected_loc,
                        priority=selected_priority,
                        description=desc_text,
                    )
                    if success:
                        st.success(f"{msg} — Ready for dispatch.")
                        st.rerun()
                    else:
                        st.warning(msg)

    # Incident Queue Filter and Table
    st.markdown(
        """
        <div class="mr-panel-header" style="margin-top: 1rem;">
            <div>
                <span class="mr-panel-title">Emergency Incident Queue</span>
                <div class="mr-panel-subtitle">Sortable triage queue across all simulation states</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    filt_col1, filt_col2 = st.columns(2)
    with filt_col1:
        status_filter = st.selectbox("Status Filter", ["All", "Pending", "Assigned", "Completed"])
    with filt_col2:
        priority_filter = st.selectbox("Priority Filter", ["All", "Critical", "High", "Medium", "Low"])

    filtered_incidents = list(incidents.values())
    if status_filter != "All":
        filtered_incidents = [i for i in filtered_incidents if i.status == status_filter]
    if priority_filter != "All":
        filtered_incidents = [i for i in filtered_incidents if i.priority == priority_filter]

    filtered_incidents.sort(key=lambda i: (0 if i.is_pending else (1 if i.status == "Assigned" else 2), i.priority_rank))

    if not filtered_incidents:
        st.info("No emergency calls match the filter criteria.")
    else:
        table_records = []
        for inc in filtered_incidents:
            node_obj = state.network.get_node(inc.location)
            loc_label = f"{inc.location} ({node_obj.label if node_obj else ''})"
            table_records.append(
                {
                    "Incident ID": inc.id,
                    "Priority": inc.priority,
                    "Location": loc_label,
                    "Status": inc.status,
                    "Assigned Unit": inc.assigned_ambulance_id or "—",
                    "Simulated Travel": f"{inc.simulated_travel_time:.1f} min" if inc.simulated_travel_time else "—",
                    "Reported Time": inc.created_at,
                    "Description": inc.description,
                }
            )

        df_display = pd.DataFrame(table_records)
        st.dataframe(df_display, hide_index=True, use_container_width=True)

    render_disclaimer()


if __name__ == "__main__":
    main()
