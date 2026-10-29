"""Simulation package for MediRoute."""

from simulation.ambulances import Ambulance, generate_default_ambulances
from simulation.incidents import (
    Incident,
    PRIORITY_COLORS,
    PRIORITY_ORDER,
    generate_default_incidents,
    validate_incident_input,
)
from simulation.simulator import (
    advance_simulation_step,
    dispatch_history_to_dataframe,
    fleet_to_dataframe,
    incidents_to_dataframe,
    return_all_ambulances_home,
    trigger_emergency_surge,
)
from simulation.state_manager import (
    SimulationState,
    get_simulation_state,
    reset_global_simulation,
)

__all__ = [
    "Ambulance",
    "generate_default_ambulances",
    "Incident",
    "PRIORITY_ORDER",
    "PRIORITY_COLORS",
    "generate_default_incidents",
    "validate_incident_input",
    "SimulationState",
    "get_simulation_state",
    "reset_global_simulation",
    "trigger_emergency_surge",
    "advance_simulation_step",
    "return_all_ambulances_home",
    "dispatch_history_to_dataframe",
    "fleet_to_dataframe",
    "incidents_to_dataframe",
]
