"""MediRoute — Algorithm Analytics & Benchmarking Suite (Page 7).

Provides empirical Dijkstra runtime scalability benchmarks, explored node metrics,
fleet utilization analytics, and CSV data export controls.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd

from simulation.simulator import dispatch_history_to_dataframe, fleet_to_dataframe
from simulation.state_manager import get_simulation_state
from ui.auth import require_authentication
from ui.components import render_command_bar, render_disclaimer, render_kpi_card
from ui.styles import apply_custom_styles
from visualization.performance import (
    build_benchmark_runtime_chart,
    build_explored_nodes_chart,
    build_fleet_utilization_chart,
    build_priority_distribution_chart,
    run_dijkstra_scalability_benchmark,
)


def main():
    st.set_page_config(page_title="MediRoute — Algorithm Analytics", page_icon="✚", layout="wide")
    apply_custom_styles()
    require_authentication()
    state = get_simulation_state()
    metrics = state.get_summary_metrics()

    render_command_bar(
        title="Algorithm Analytics",
        subtitle="Empirical Complexity Profiling, Explored Vertex Auditing, & Export Reports",
        show_dispatch_btn=True,
        simulation_step=metrics["simulation_step"],
    )

    # Top KPI Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Total Dispatches", metrics["total_dispatches"], "Historical runs", "#0D1B2A")
    with c2:
        render_kpi_card("Avg Travel Time", f"{metrics['average_response_time']} min", "Simulated network response", "#0F9D92")
    with c3:
        render_kpi_card("Graph Vertices |V|", len(state.network.nodes), "Current network order", "#16A34A")
    with c4:
        render_kpi_card("Graph Edges |E|", len(state.network.edges), "Current network size", "#64748B")

    # Benchmark Execution Section
    st.markdown(
        """
        <div class="mr-panel-header" style="margin-top: 0.5rem;">
            <div>
                <span class="mr-panel-title">Dijkstra Scalability Benchmark Suite</span>
                <div class="mr-panel-subtitle">Profiles Dijkstra execution time across synthetic graph topologies of cardinality |V| &isin; [10, 100]</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "bench_df" not in st.session_state:
        st.session_state["bench_df"] = run_dijkstra_scalability_benchmark([10, 20, 35, 50, 75, 100], repeats=3)

    if st.button("Re-Run Live Empirical Benchmark Suite"):
        with st.spinner("Executing Dijkstra trials across graph topologies..."):
            st.session_state["bench_df"] = run_dijkstra_scalability_benchmark([10, 20, 35, 50, 75, 100], repeats=5)
            st.success("Benchmark completed successfully.")

    df_bench = st.session_state["bench_df"]

    # Charts side-by-side
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(build_benchmark_runtime_chart(df_bench), use_container_width=True)
    with chart_col2:
        st.plotly_chart(build_explored_nodes_chart(df_bench), use_container_width=True)

    with st.expander("View Benchmark Raw Measurement Data Table", expanded=False):
        st.dataframe(df_bench, hide_index=True, use_container_width=True)

    # Fleet & Incident Queue Breakdown
    st.markdown(
        """
        <div class="mr-panel-header" style="margin-top: 1rem;">
            <div>
                <span class="mr-panel-title">Fleet Telemetry & Incident Distributions</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fleet_col, prio_col = st.columns(2)
    with fleet_col:
        st.plotly_chart(build_fleet_utilization_chart(state.ambulances), use_container_width=True)
    with prio_col:
        st.plotly_chart(build_priority_distribution_chart(state.incidents), use_container_width=True)

    # CSV Data Export Center
    st.markdown(
        """
        <div class="mr-panel-header" style="margin-top: 1rem;">
            <div>
                <span class="mr-panel-title">CSV Data Export Center</span>
                <div class="mr-panel-subtitle">Download audit logs and benchmark measurements</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    exp_col1, exp_col2, exp_col3 = st.columns(3)

    with exp_col1:
        st.markdown("<strong>1. Dispatch History Log</strong>", unsafe_allow_html=True)
        st.caption("Complete audit record of committed emergency dispatches, routes, and response times.")
        df_hist = dispatch_history_to_dataframe(state)
        csv_hist = df_hist.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Dispatch Log (CSV)",
            data=csv_hist,
            file_name="mediroute_dispatch_history.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with exp_col2:
        st.markdown("<strong>2. Benchmark Measurements</strong>", unsafe_allow_html=True)
        st.caption("Empirical microsecond runtime and explored node statistics across tested graph sizes.")
        csv_bench = df_bench.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Benchmark Results (CSV)",
            data=csv_bench,
            file_name="mediroute_benchmark_results.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with exp_col3:
        st.markdown("<strong>3. Fleet Status Snapshot</strong>", unsafe_allow_html=True)
        st.caption("Telemetry snapshot of all ambulances, stations, medical capabilities, and missions.")
        df_fleet = fleet_to_dataframe(state)
        csv_fleet = df_fleet.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Fleet Snapshot (CSV)",
            data=csv_fleet,
            file_name="mediroute_fleet_snapshot.csv",
            mime="text/csv",
            use_container_width=True,
        )

    render_disclaimer()


if __name__ == "__main__":
    main()
