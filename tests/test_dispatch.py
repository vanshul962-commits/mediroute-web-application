"""Unit tests for the Greedy Dispatch Engine strategies."""

import pytest
from algorithms.greedy_dispatch import (
    greedy_batch_dispatch,
    nearest_available_dispatch,
    priority_aware_dispatch,
)
from graph.sample_network import build_default_metro_network, build_disconnected_network
from simulation.ambulances import Ambulance
from simulation.incidents import Incident


@pytest.fixture
def test_fleet():
    """Create a minimal controlled fleet for dispatch testing."""
    return {
        "AMB-A": Ambulance(
            id="AMB-A",
            call_sign="Alpha-1",
            current_node="STA_ALPHA",
            status="Available",
            capability="ALS",
        ),
        "AMB-B": Ambulance(
            id="AMB-B",
            call_sign="Beta-1",
            current_node="STA_BETA",
            status="Available",
            capability="BLS",
        ),
        "AMB-BUSY": Ambulance(
            id="AMB-BUSY",
            call_sign="Busy-1",
            current_node="INT_DOWNTOWN",
            status="Busy",
            capability="ALS",
        ),
    }


def test_nearest_available_selection(test_fleet):
    """Verify that nearest ambulance is chosen and busy ambulance is ignored."""
    net = build_default_metro_network()
    # Incident at INT_NORTH_GATE is directly adjacent to STA_ALPHA (AMB-A)
    incident = Incident(
        id="INC-T1",
        location="INT_NORTH_GATE",
        priority="Medium",
        description="Test incident",
    )

    res = nearest_available_dispatch(net, incident, test_fleet)
    assert res.is_successful
    assert res.selected_ambulance_id == "AMB-A"
    assert res.estimated_travel_time is not None
    assert res.estimated_travel_time < 5.0
    assert "AMB-BUSY" not in [c.ambulance_id for c in res.candidates if c.eligible]


def test_no_available_ambulances():
    """Verify clean response when entire fleet is busy."""
    net = build_default_metro_network()
    incident = Incident(id="INC-T2", location="INT_DOWNTOWN", priority="High", description="Test")
    all_busy_fleet = {
        "AMB-1": Ambulance(id="AMB-1", call_sign="A1", current_node="STA_ALPHA", status="Busy"),
    }
    res = nearest_available_dispatch(net, incident, all_busy_fleet)
    assert not res.is_successful
    assert res.status == "NO_AVAILABLE_AMBULANCES"
    assert "All simulated ambulances are currently busy" in res.explanation


def test_unreachable_incident():
    """Verify handling when an incident is in a disconnected island component."""
    net = build_disconnected_network()
    fleet = {
        "AMB-1": Ambulance(id="AMB-1", call_sign="M1", current_node="C1_NODE_A", status="Available"),
    }
    incident = Incident(id="INC-T3", location="C2_NODE_Y", priority="High", description="Island call")
    res = nearest_available_dispatch(net, incident, fleet)
    assert not res.is_successful
    assert res.status == "UNREACHABLE"
    assert "None of the 1 available ambulances can reach" in res.explanation


def test_priority_aware_critical_als_preference():
    """Verify Priority-Aware strategy prioritizes ALS capability for Critical incidents."""
    net = build_default_metro_network()
    # Both ambulances placed at same node or similar distance
    fleet = {
        "AMB-BLS": Ambulance(
            id="AMB-BLS",
            call_sign="BLS Unit",
            current_node="INT_MIDTOWN",
            status="Available",
            capability="BLS",
        ),
        "AMB-ALS": Ambulance(
            id="AMB-ALS",
            call_sign="ALS Unit",
            current_node="INT_MIDTOWN",
            status="Available",
            capability="ALS",
        ),
    }
    critical_incident = Incident(
        id="INC-CRIT",
        location="HOSP_CENTRAL",
        priority="Critical",
        description="Cardiac arrest",
    )

    res = priority_aware_dispatch(net, critical_incident, fleet)
    assert res.is_successful
    assert res.selected_ambulance_id == "AMB-ALS"
    assert "ALS Capable" in res.explanation


def test_greedy_batch_dispatch_no_duplicate_assignments():
    """Verify batch dispatch assigns each vehicle at most once, in strict priority order."""
    net = build_default_metro_network()
    fleet = {
        "AMB-1": Ambulance(id="AMB-1", call_sign="A1", current_node="STA_ALPHA", status="Available"),
        "AMB-2": Ambulance(id="AMB-2", call_sign="A2", current_node="STA_BETA", status="Available"),
    }
    # 3 pending incidents, but only 2 ambulances exist
    incidents = [
        Incident(id="INC-1", location="INT_NORTH_GATE", priority="Low", description="Low 1"),
        Incident(id="INC-2", location="INT_UNIVERSITY", priority="Critical", description="Critical 1"),
        Incident(id="INC-3", location="INT_DOWNTOWN", priority="High", description="High 1"),
    ]

    batch_res = greedy_batch_dispatch(net, incidents, fleet)
    # 2 assignments possible, 1 unassigned
    assert len(batch_res.assignments) == 2
    assert len(batch_res.unassigned_incidents) == 1

    assigned_amb_ids = [a.selected_ambulance_id for a in batch_res.assignments]
    assert len(assigned_amb_ids) == len(set(assigned_amb_ids)), "Duplicate ambulance assignment occurred!"

    # First assignment must be for the Critical incident (INC-2)
    assert batch_res.assignments[0].incident_id == "INC-2"
    # Second assignment must be for the High incident (INC-3)
    assert batch_res.assignments[1].incident_id == "INC-3"
    # The Low incident (INC-1) was left unassigned due to fleet exhaustion
    assert batch_res.unassigned_incidents[0][0] == "INC-1"
