"""Simulation Engine and Scenario Generators for MediRoute.

Provides automated step transitions, surge generators, and dataframe export
helpers for analytics and CSV downloads.
"""

from __future__ import annotations
import random
from typing import Any, Dict, List, Optional
import pandas as pd

from algorithms.dijkstra import dijkstra_shortest_path
from simulation.incidents import Incident, PRIORITY_ORDER
from simulation.state_manager import SimulationState


def trigger_emergency_surge(state: SimulationState, count: int = 3) -> List[Incident]:
    """Generate a burst of realistic synthetic emergency calls across the city grid."""
    intersections = state.network.intersections()
    if not intersections:
        intersections = list(state.network.nodes.keys())

    priorities = ["Critical", "High", "High", "Medium", "Medium", "Low"]
    descriptions = [
        "Simulated sudden chest pain and respiratory distress reported",
        "Simulated two-vehicle collision with minor roadway obstruction",
        "Simulated fall from height at construction renovation site",
        "Simulated severe allergic reaction at downtown dining area",
        "Simulated elderly wellness check and non-emergency transport",
        "Simulated multi-vehicle fender bender during peak transit hours",
    ]

    new_incidents: List[Incident] = []
    for _ in range(count):
        loc = random.choice(intersections)
        prio = random.choice(priorities)
        desc = random.choice(descriptions)
        success, msg, inc = state.add_new_incident(loc, prio, desc)
        if success and inc:
            new_incidents.append(inc)

    return new_incidents


def advance_simulation_step(state: SimulationState) -> str:
    """Advance the simulation time-step by 1.

    Completes any actively assigned incident where the simulated time elapsed,
    allowing busy ambulances to transition back to Available.
    """
    assigned_incidents = [inc for inc in state.incidents.values() if inc.status == "Assigned"]
    if not assigned_incidents:
        state.simulation_step += 1
        return "Simulation advanced by 1 interval. No active dispatches required resolution."

    # Complete the oldest assigned incident
    target_inc = assigned_incidents[0]
    success, msg = state.complete_mission(target_inc.id, return_to_hospital=True)
    return msg


def return_all_ambulances_home(state: SimulationState) -> int:
    """Return all idle and busy ambulances back to their home stations."""
    count = 0
    for amb in state.ambulances.values():
        amb.return_to_station()
        count += 1
    # Mark assigned incidents completed or pending
    for inc in state.incidents.values():
        if inc.status == "Assigned":
            inc.status = "Pending"
            inc.assigned_ambulance_id = None
            inc.route = None
    state.simulation_step += 1
    return count


def dispatch_history_to_dataframe(state: SimulationState) -> pd.DataFrame:
    """Convert dispatch history records into a clean Pandas DataFrame for display & CSV export."""
    if not state.dispatch_history:
        return pd.DataFrame(
            columns=[
                "dispatch_id",
                "timestamp",
                "incident_id",
                "incident_priority",
                "ambulance_id",
                "call_sign",
                "strategy",
                "route",
                "simulated_travel_time",
                "computation_time_ms",
                "status",
            ]
        )

    records = []
    for d in state.dispatch_history:
        rec = dict(d)
        if isinstance(rec.get("route"), list):
            rec["route"] = " -> ".join(rec["route"])
        records.append(rec)
    return pd.DataFrame(records)


def fleet_to_dataframe(state: SimulationState) -> pd.DataFrame:
    """Convert ambulance fleet to a Pandas DataFrame."""
    records = []
    for a in state.ambulances.values():
        records.append(
            {
                "Ambulance ID": a.id,
                "Call Sign": a.call_sign,
                "Current Location": a.current_node,
                "Home Station": a.home_station,
                "Status": a.status,
                "Capability": a.capability,
                "Assignments Done": a.assignments_completed,
                "Active Incident": a.current_assigned_incident or "None",
                "Total Travel Time (min)": round(a.total_travel_time_simulated, 1),
            }
        )
    return pd.DataFrame(records)


def incidents_to_dataframe(state: SimulationState) -> pd.DataFrame:
    """Convert incidents dictionary to a Pandas DataFrame."""
    records = []
    for i in state.incidents.values():
        records.append(
            {
                "Incident ID": i.id,
                "Priority": i.priority,
                "Location": i.location,
                "Status": i.status,
                "Assigned Unit": i.assigned_ambulance_id or "-",
                "Simulated Travel (min)": f"{i.simulated_travel_time:.1f}" if i.simulated_travel_time else "-",
                "Description": i.description,
                "Reported At": i.created_at,
            }
        )
    return pd.DataFrame(records)
