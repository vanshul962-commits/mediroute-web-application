"""Performance Benchmarking and Analytical Visualizations for MediRoute.

Provides functions to run real algorithm benchmarks across synthetic graph sizes,
and generate Plotly charts for execution times, explored node counts, fleet
utilization, and strategy comparisons.
"""

from __future__ import annotations
import time
from typing import Any, Dict, List, Tuple
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from algorithms.dijkstra import dijkstra_shortest_path
from graph.sample_network import generate_random_network
from simulation.ambulances import Ambulance
from simulation.incidents import Incident, PRIORITY_COLORS


def run_dijkstra_scalability_benchmark(
    node_sizes: List[int] = [10, 20, 35, 50, 75, 100],
    repeats: int = 5,
) -> pd.DataFrame:
    """Benchmark Dijkstra algorithm across synthetic graph sizes with repeated trials."""
    records: List[Dict[str, Any]] = []

    for n in node_sizes:
        net = generate_random_network(seed=100 + n, num_nodes=n, connectivity=0.28)
        node_ids = net.node_ids()
        if len(node_ids) < 2:
            continue

        src = node_ids[0]
        dst = node_ids[-1]

        runtimes: List[float] = []
        explored_counts: List[int] = []
        path_costs: List[float] = []

        for _ in range(repeats):
            res = dijkstra_shortest_path(net.adjacency, src, dst)
            runtimes.append(res.execution_time_ms)
            explored_counts.append(res.explored_nodes)
            if res.found:
                path_costs.append(res.total_cost)

        avg_time = sum(runtimes) / len(runtimes)
        min_time = min(runtimes)
        max_time = max(runtimes)
        avg_explored = sum(explored_counts) / len(explored_counts)

        records.append(
            {
                "Node Count (|V|)": n,
                "Edge Count (|E|)": len(net.edges),
                "Average Runtime (ms)": round(avg_time, 4),
                "Min Runtime (ms)": round(min_time, 4),
                "Max Runtime (ms)": round(max_time, 4),
                "Avg Explored Nodes": round(avg_explored, 1),
                "Exploration Ratio (%)": round((avg_explored / n) * 100, 1),
                "Theoretical O((V+E)logV)": round((n + len(net.edges)) * (n ** 0.5) * 0.001, 3),
            }
        )

    return pd.DataFrame(records)


def build_benchmark_runtime_chart(df_bench: pd.DataFrame) -> go.Figure:
    """Create a line chart showing Dijkstra execution time vs Graph Size |V|."""
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_bench["Node Count (|V|)"],
            y=df_bench["Average Runtime (ms)"],
            mode="lines+markers",
            name="Empirical Dijkstra Runtime",
            line=dict(color="#0F9D92", width=3),
            marker=dict(size=8, color="#10243A"),
            error_y=dict(
                type="data",
                symmetric=False,
                array=(df_bench["Max Runtime (ms)"] - df_bench["Average Runtime (ms)"]).clip(lower=0),
                arrayminus=(df_bench["Average Runtime (ms)"] - df_bench["Min Runtime (ms)"]).clip(lower=0),
                color="#667085",
                thickness=1.2,
                width=4,
            ),
            hovertemplate=(
                "<b>Nodes (|V|):</b> %{x}<br>"
                "<b>Avg Time:</b> %{y:.4f} ms<br>"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=dict(
            text="<b>Dijkstra Execution Time vs. Graph Vertices |V|</b>",
            font=dict(size=14, color="#10243A"),
        ),
        xaxis=dict(title="Graph Size (Number of Vertices |V|)", gridcolor="#E4E7EC"),
        yaxis=dict(title="Execution Time (milliseconds)", gridcolor="#E4E7EC"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=40, b=20),
        height=380,
    )
    return fig


def build_explored_nodes_chart(df_bench: pd.DataFrame) -> go.Figure:
    """Create a grouped bar chart comparing Total Vertices vs Explored Vertices."""
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df_bench["Node Count (|V|)"],
            y=df_bench["Node Count (|V|)"],
            name="Total Vertices (|V|)",
            marker_color="#D0D5DD",
        )
    )
    fig.add_trace(
        go.Bar(
            x=df_bench["Node Count (|V|)"],
            y=df_bench["Avg Explored Nodes"],
            name="Explored / Finalized Vertices",
            marker_color="#0F9D92",
        )
    )

    fig.update_layout(
        title=dict(
            text="<b>Dijkstra Pruning & Explored Vertices Efficiency</b>",
            font=dict(size=14, color="#10243A"),
        ),
        barmode="group",
        xaxis=dict(title="Network Vertices (|V|)", gridcolor="#E4E7EC"),
        yaxis=dict(title="Count of Vertices", gridcolor="#E4E7EC"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
    )
    return fig


def build_fleet_utilization_chart(ambulances: Dict[str, Ambulance]) -> go.Figure:
    """Create a donut chart illustrating ambulance status distribution."""
    status_counts = {"Available": 0, "Busy": 0, "Maintenance": 0}
    for a in ambulances.values():
        if a.status in status_counts:
            status_counts[a.status] += 1
        else:
            status_counts[a.status] = 1

    labels = list(status_counts.keys())
    values = list(status_counts.values())
    colors = ["#16A36A", "#E6A23C", "#667085"]  # Success green, Amber, Slate

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.6,
                marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
                textinfo="label+value",
                hoverinfo="label+percent",
            )
        ]
    )

    fig.update_layout(
        title=dict(text="<b>Fleet Availability</b>", font=dict(size=14, color="#10243A")),
        showlegend=False,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=10, r=10, t=35, b=10),
        height=260,
    )
    return fig


def build_priority_distribution_chart(incidents: Dict[str, Incident]) -> go.Figure:
    """Create a horizontal bar chart displaying incidents categorized by priority level."""
    prio_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for inc in incidents.values():
        if inc.priority in prio_counts:
            prio_counts[inc.priority] += 1

    categories = list(prio_counts.keys())
    counts = [prio_counts[c] for c in categories]
    colors = [PRIORITY_COLORS.get(c, "#667085") for c in categories]

    fig = go.Figure(
        data=[
            go.Bar(
                x=counts,
                y=categories,
                orientation="h",
                marker=dict(color=colors),
                text=counts,
                textposition="auto",
            )
        ]
    )

    fig.update_layout(
        title=dict(text="<b>Incidents by Priority</b>", font=dict(size=14, color="#10243A")),
        xaxis=dict(title="Number of Calls", gridcolor="#E4E7EC"),
        yaxis=dict(autorange="reversed"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=10, r=10, t=35, b=10),
        height=260,
    )
    return fig


def build_candidate_comparison_chart(candidates: List[Any]) -> go.Figure:
    """Bar chart comparing simulated travel times for evaluated ambulance candidates."""
    eligible = [c for c in candidates if getattr(c, "eligible", False)]
    if not eligible:
        fig = go.Figure()
        fig.add_annotation(text="No eligible candidates to compare", showarrow=False)
        return fig

    amb_names = [f"{c.ambulance_id} ({c.call_sign})" for c in eligible]
    times = [c.travel_time for c in eligible]
    colors = ["#0F9D92" if idx == 0 else "#667085" for idx in range(len(eligible))]

    fig = go.Figure(
        data=[
            go.Bar(
                x=amb_names,
                y=times,
                marker=dict(color=colors),
                text=[f"{t:.1f} min" for t in times],
                textposition="auto",
            )
        ]
    )

    fig.update_layout(
        title=dict(text="<b>Candidate Simulated Travel Times (Minutes)</b>", font=dict(size=13, color="#10243A")),
        xaxis=dict(title="Candidate Ambulance"),
        yaxis=dict(title="Simulated Minutes", gridcolor="#E4E7EC"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=15, r=15, t=35, b=15),
        height=280,
    )
    return fig
