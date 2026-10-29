"""Unit tests for the SimulationState manager and state transitions."""

import pytest
from simulation.state_manager import SimulationState


def test_simulation_state_initialization():
    """Verify default simulation state initializes cleanly with expected defaults."""
    state = SimulationState.create_default()
    assert len(state.network.nodes) == 20
    assert len(state.ambulances) == 6
    assert len(state.incidents) >= 4
    metrics = state.get_summary_metrics()
    assert metrics["total_ambulances"] == 6
    assert metrics["available_ambulances"] == 5
    assert metrics["busy_ambulances"] == 1


def test_commit_dispatch_success_and_duplicate_prevention():
    """Verify state transitions when committing dispatch, and duplicate rejection."""
    state = SimulationState.create_default()
    # Find an available ambulance and a pending incident
    amb = state.ambulances["AMB-01"]
    inc = state.incidents["INC-101"]

    assert amb.is_available
    assert inc.is_pending

    route = ["STA_ALPHA", "INT_NORTH_GATE", "INT_MIDTOWN", "HOSP_CENTRAL", "INT_DOWNTOWN"]
    success, msg = state.commit_dispatch(
        incident_id=inc.id,
        ambulance_id=amb.id,
        strategy="Nearest Available",
        route=route,
        travel_time=12.6,
        computation_time_ms=0.55,
    )

    assert success is True
    assert not amb.is_available
    assert amb.status == "Busy"
    assert inc.status == "Assigned"
    assert inc.assigned_ambulance_id == amb.id

    # Attempting to re-dispatch the same busy ambulance to another call must fail
    success2, msg2 = state.commit_dispatch(
        incident_id="INC-102",
        ambulance_id=amb.id,
        strategy="Nearest Available",
        route=["STA_ALPHA", "INT_TECH_PARK"],
        travel_time=15.0,
    )
    assert success2 is False
    assert "currently Busy" in msg2

    # Attempting to assign an already assigned incident must fail
    success3, msg3 = state.commit_dispatch(
        incident_id=inc.id,
        ambulance_id="AMB-02",
        strategy="Nearest Available",
        route=["STA_ALPHA", "INT_DOWNTOWN"],
        travel_time=14.0,
    )
    assert success3 is False
    assert "already Assigned" in msg3


def test_complete_mission_and_vehicle_release():
    """Verify mission completion cycle releases ambulance and updates location."""
    state = SimulationState.create_default()
    # Complete existing assigned incident INC-100
    inc = state.incidents["INC-100"]
    amb = state.ambulances[inc.assigned_ambulance_id]
    assert amb.status == "Busy"

    completed_before = amb.assignments_completed
    success, msg = state.complete_mission(inc.id, return_to_hospital=True)

    assert success is True
    assert inc.status == "Completed"
    assert amb.status == "Available"
    assert amb.assignments_completed == completed_before + 1


def test_add_new_incident_and_duplicate_prevention():
    """Verify synthetic incident creation and deduplication."""
    state = SimulationState.create_default()
    success, msg, inc = state.add_new_incident(
        location="INT_MIDTOWN",
        priority="Critical",
        description="Simulated trauma collision",
    )
    assert success is True
    assert inc is not None
    assert inc.id.startswith("INC-")
    assert inc.location == "INT_MIDTOWN"

    # Exact duplicate pending at same location with same description rejected
    dup_success, dup_msg, _ = state.add_new_incident(
        location="INT_MIDTOWN",
        priority="Critical",
        description="Simulated trauma collision",
    )
    assert dup_success is False
    assert "Duplicate incident already pending" in dup_msg


def test_reset_to_defaults():
    """Verify that resetting state restores all pristine default collections."""
    state = SimulationState.create_default()
    # Mutate state
    state.ambulances.clear()
    state.incidents.clear()
    assert len(state.ambulances) == 0

    state.reset_to_defaults()
    assert len(state.ambulances) == 6
    assert len(state.incidents) >= 4
