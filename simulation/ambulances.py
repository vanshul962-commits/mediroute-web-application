"""Ambulance Fleet Management Models and Default Fleet for MediRoute.

Defines the `Ambulance` dataclass and functions for fleet initialization,
status transitions, and assignment tracking.
"""

from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Ambulance:
    """Represents an emergency medical response vehicle in the simulation."""

    id: str
    call_sign: str
    current_node: str
    status: str = "Available"  # "Available", "Busy", "Maintenance"
    capability: str = "ALS"  # "ALS" (Advanced Life Support), "BLS" (Basic Life Support)
    assignments_completed: int = 0
    current_assigned_incident: Optional[str] = None
    total_travel_time_simulated: float = 0.0
    home_station: str = "STA_ALPHA"

    @property
    def is_available(self) -> bool:
        """Return True only if the ambulance is ready for immediate dispatch."""
        return self.status == "Available"

    def assign(self, incident_id: str, travel_time: float) -> None:
        """Mark ambulance as busy and assign to an incident.

        Raises:
            ValueError: If ambulance is not currently available.
        """
        if not self.is_available:
            raise ValueError(f"Ambulance {self.id} cannot be assigned: currently {self.status}")
        self.status = "Busy"
        self.current_assigned_incident = incident_id
        self.total_travel_time_simulated += travel_time

    def complete(self, new_location: Optional[str] = None) -> None:
        """Mark assigned mission complete and return ambulance to available pool."""
        self.status = "Available"
        self.current_assigned_incident = None
        self.assignments_completed += 1
        if new_location:
            self.current_node = new_location

    def return_to_station(self) -> None:
        """Return ambulance to its designated home station."""
        self.current_node = self.home_station
        self.status = "Available"
        self.current_assigned_incident = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Ambulance:
        """Construct from dictionary."""
        return cls(**data)


def generate_default_ambulances() -> Dict[str, Ambulance]:
    """Generate the initial fleet of 6 simulated emergency vehicles distributed across stations."""
    fleet = [
        Ambulance(
            id="AMB-01",
            call_sign="Rescue Alpha-1",
            current_node="STA_ALPHA",
            home_station="STA_ALPHA",
            status="Available",
            capability="ALS",
            assignments_completed=2,
            total_travel_time_simulated=14.5,
        ),
        Ambulance(
            id="AMB-02",
            call_sign="Medic Alpha-2",
            current_node="STA_ALPHA",
            home_station="STA_ALPHA",
            status="Available",
            capability="BLS",
            assignments_completed=1,
            total_travel_time_simulated=7.2,
        ),
        Ambulance(
            id="AMB-03",
            call_sign="Rescue Beta-1",
            current_node="STA_BETA",
            home_station="STA_BETA",
            status="Available",
            capability="ALS",
            assignments_completed=3,
            total_travel_time_simulated=22.0,
        ),
        Ambulance(
            id="AMB-04",
            call_sign="Medic Beta-2",
            current_node="STA_BETA",
            home_station="STA_BETA",
            status="Busy",
            capability="BLS",
            assignments_completed=4,
            current_assigned_incident="INC-100",
            total_travel_time_simulated=31.4,
        ),
        Ambulance(
            id="AMB-05",
            call_sign="Rescue Gamma-1",
            current_node="STA_GAMMA",
            home_station="STA_GAMMA",
            status="Available",
            capability="ALS",
            assignments_completed=1,
            total_travel_time_simulated=8.5,
        ),
        Ambulance(
            id="AMB-06",
            call_sign="Medic Gamma-2",
            current_node="STA_GAMMA",
            home_station="STA_GAMMA",
            status="Available",
            capability="BLS",
            assignments_completed=0,
            total_travel_time_simulated=0.0,
        ),
    ]
    return {amb.id: amb for amb in fleet}
