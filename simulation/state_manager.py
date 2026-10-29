"""Session State Management and State Purity for MediRoute.

Provides thread-safe, rerun-safe simulation state handling with a clean separation
between pure state data (`SimulationState`) and Streamlit's `st.session_state`.
"""

from __future__ import annotations
import copy
import datetime
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from algorithms.dijkstra import dijkstra_shortest_path
from graph.graph_utils import RoadNetwork
from graph.sample_network import build_default_metro_network
from simulation.ambulances import Ambulance, generate_default_ambulances
from simulation.incidents import Incident, generate_default_incidents


@dataclass
class SimulationState:
    """Encapsulates all mutable state for the MediRoute simulation."""

    network: RoadNetwork
    ambulances: Dict[str, Ambulance]
    incidents: Dict[str, Incident]
    dispatch_history: List[Dict[str, Any]] = field(default_factory=list)
    benchmark_runs: List[Dict[str, Any]] = field(default_factory=list)
    incident_counter: int = 105
    simulation_step: int = 0

    @classmethod
    def create_default(cls) -> SimulationState:
        """Create a fresh, deterministic default simulation state."""
        net = build_default_metro_network()
        ambs = generate_default_ambulances()
        incs = generate_default_incidents()
        initial_history = [
            {
                "dispatch_id": "DISP-001",
                "timestamp": "17:20:10",
                "incident_id": "INC-100",
                "incident_priority": "High",
                "ambulance_id": "AMB-04",
                "call_sign": "Medic Beta-2",
                "strategy": "Nearest Available",
                "route": ["STA_BETA", "INT_HARBOR_VIEW"],
                "simulated_travel_time": 2.2,
                "computation_time_ms": 0.42,
                "status": "Committed",
            }
        ]
        return cls(
            network=net,
            ambulances=ambs,
            incidents=incs,
            dispatch_history=initial_history,
            benchmark_runs=[],
            incident_counter=105,
            simulation_step=1,
        )

    def commit_dispatch(
        self,
        incident_id: str,
        ambulance_id: str,
        strategy: str,
        route: List[str],
        travel_time: float,
        computation_time_ms: float = 0.0,
    ) -> Tuple[bool, str]:
        """Atomically commit an ambulance dispatch to an incident.

        Validations:
        1. Incident exists and is currently in 'Pending' status.
        2. Ambulance exists and is currently in 'Available' status.
        3. Route is non-empty and connects ambulance location to incident location.

        Returns:
            Tuple of (success_boolean, human_readable_message).
        """
        # Validate incident
        if incident_id not in self.incidents:
            return False, f"Incident '{incident_id}' does not exist."
        incident = self.incidents[incident_id]
        if not incident.is_pending:
            return False, f"Incident '{incident_id}' is already {incident.status}."

        # Validate ambulance
        if ambulance_id not in self.ambulances:
            return False, f"Ambulance '{ambulance_id}' does not exist."
        ambulance = self.ambulances[ambulance_id]
        if not ambulance.is_available:
            return False, f"Ambulance '{ambulance_id}' is currently {ambulance.status}."

        # Validate route
        if not route or route[0] != ambulance.current_node or route[-1] != incident.location:
            return False, (
                f"Invalid route: expected start at '{ambulance.current_node}' and end at '{incident.location}'. "
                f"Route provided: {route}"
            )

        # Apply state transitions atomically
        ambulance.assign(incident_id=incident.id, travel_time=travel_time)
        incident.assign_ambulance(
            ambulance_id=ambulance.id,
            strategy=strategy,
            travel_time=travel_time,
            route=route,
        )

        dispatch_record = {
            "dispatch_id": f"DISP-{len(self.dispatch_history) + 1:03d}",
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "incident_id": incident.id,
            "incident_priority": incident.priority,
            "ambulance_id": ambulance.id,
            "call_sign": ambulance.call_sign,
            "strategy": strategy,
            "route": route,
            "simulated_travel_time": round(travel_time, 2),
            "computation_time_ms": round(computation_time_ms, 4),
            "status": "Committed",
        }
        self.dispatch_history.append(dispatch_record)
        self.simulation_step += 1

        return True, f"Successfully dispatched {ambulance.id} to incident {incident.id} ({travel_time:.1f} min travel time)."

    def complete_mission(
        self,
        incident_id: str,
        return_to_hospital: bool = True,
    ) -> Tuple[bool, str]:
        """Mark an active dispatch completed, returning ambulance to available pool."""
        if incident_id not in self.incidents:
            return False, f"Incident '{incident_id}' does not exist."
        incident = self.incidents[incident_id]
        if incident.status != "Assigned":
            return False, f"Incident '{incident_id}' is currently {incident.status}; only 'Assigned' can be completed."

        amb_id = incident.assigned_ambulance_id
        if not amb_id or amb_id not in self.ambulances:
            return False, f"No registered ambulance assigned to {incident_id}."

        ambulance = self.ambulances[amb_id]

        # Determine next destination for ambulance
        new_node = incident.location
        if return_to_hospital:
            # Find nearest hospital from incident site
            hospitals = self.network.hospitals()
            if hospitals:
                best_hosp = hospitals[0]
                min_cost = float("inf")
                for h in hospitals:
                    res = dijkstra_shortest_path(self.network.adjacency, incident.location, h)
                    if res.found and res.total_cost < min_cost:
                        min_cost = res.total_cost
                        best_hosp = h
                new_node = best_hosp

        incident.mark_completed()
        ambulance.complete(new_location=new_node)
        self.simulation_step += 1

        return True, f"Incident {incident.id} marked completed. {ambulance.id} transported patient to {new_node} and is now Available."

    def add_new_incident(
        self,
        location: str,
        priority: str,
        description: str,
    ) -> Tuple[bool, str, Optional[Incident]]:
        """Create and register a new synthetic emergency call."""
        if location not in self.network.nodes:
            return False, f"Location '{location}' is not on the road network.", None

        # Check for exact duplicate pending incident at identical location
        for inc in self.incidents.values():
            if inc.is_pending and inc.location == location and inc.description == description:
                return False, f"Duplicate incident already pending at {location}.", None

        inc_id = f"INC-{self.incident_counter}"
        self.incident_counter += 1

        new_inc = Incident(
            id=inc_id,
            location=location,
            priority=priority,
            description=description,
            created_at=datetime.datetime.now().strftime("%H:%M:%S"),
            status="Pending",
        )
        self.incidents[inc_id] = new_inc
        self.simulation_step += 1
        return True, f"Incident {inc_id} created successfully.", new_inc

    def reset_to_defaults(self) -> None:
        """Reset the entire simulation state to pristine default values."""
        fresh = SimulationState.create_default()
        self.network = fresh.network
        self.ambulances = fresh.ambulances
        self.incidents = fresh.incidents
        self.dispatch_history = fresh.dispatch_history
        self.benchmark_runs.clear()
        self.incident_counter = fresh.incident_counter
        self.simulation_step = fresh.simulation_step

    def get_summary_metrics(self) -> Dict[str, Any]:
        """Compute key real-time metrics for dashboard cards."""
        total_ambs = len(self.ambulances)
        available_ambs = sum(1 for a in self.ambulances.values() if a.is_available)
        busy_ambs = sum(1 for a in self.ambulances.values() if a.status == "Busy")
        maintenance_ambs = sum(1 for a in self.ambulances.values() if a.status == "Maintenance")

        pending_inc = sum(1 for i in self.incidents.values() if i.is_pending)
        assigned_inc = sum(1 for i in self.incidents.values() if i.status == "Assigned")
        completed_inc = sum(1 for i in self.incidents.values() if i.status == "Completed")
        critical_pending = sum(1 for i in self.incidents.values() if i.is_pending and i.priority == "Critical")

        avg_travel_time = 0.0
        if self.dispatch_history:
            times = [d["simulated_travel_time"] for d in self.dispatch_history if "simulated_travel_time" in d]
            if times:
                avg_travel_time = round(sum(times) / len(times), 1)

        return {
            "total_ambulances": total_ambs,
            "available_ambulances": available_ambs,
            "busy_ambulances": busy_ambs,
            "maintenance_ambulances": maintenance_ambs,
            "pending_incidents": pending_inc,
            "assigned_incidents": assigned_inc,
            "completed_incidents": completed_inc,
            "critical_pending": critical_pending,
            "total_dispatches": len(self.dispatch_history),
            "average_response_time": avg_travel_time,
            "simulation_step": self.simulation_step,
        }


# =====================================================================
# Streamlit Session State Connector
# =====================================================================

SESSION_KEY = "mediroute_sim_state"


def get_simulation_state() -> SimulationState:
    """Retrieve or initialize the SimulationState stored in Streamlit session_state.

    Falls back cleanly to an in-memory singleton if run outside Streamlit.
    """
    try:
        import streamlit as st

        if SESSION_KEY not in st.session_state:
            st.session_state[SESSION_KEY] = SimulationState.create_default()
        return st.session_state[SESSION_KEY]
    except (ImportError, Exception):
        # Fallback for headless non-Streamlit environments (e.g., background scripts)
        if not hasattr(get_simulation_state, "_instance"):
            get_simulation_state._instance = SimulationState.create_default()  # type: ignore
        return get_simulation_state._instance  # type: ignore


def reset_global_simulation() -> None:
    """Reset the Streamlit session state simulation."""
    state = get_simulation_state()
    state.reset_to_defaults()
