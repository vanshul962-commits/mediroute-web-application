"""Emergency Incident Data Models and Management for MediRoute.

Defines the `Incident` dataclass, priority tiers, and initialization of
synthetic test incidents for simulation and greedy dispatch.
"""

from __future__ import annotations
import datetime
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

# Priority numerical weights: Lower rank = higher dispatch urgency
PRIORITY_ORDER: Dict[str, int] = {
    "Critical": 1,
    "High": 2,
    "Medium": 3,
    "Low": 4,
}

PRIORITY_COLORS: Dict[str, str] = {
    "Critical": "#E5484D",  # Emergency Red
    "High": "#E6A23C",      # Amber Warning
    "Medium": "#0F9D92",    # MediRoute Teal
    "Low": "#667085",       # Slate Gray
}


@dataclass
class Incident:
    """Represents a synthetic emergency call in the simulated dispatch environment."""

    id: str
    location: str  # Node ID on the road network
    priority: str  # "Critical", "High", "Medium", "Low"
    description: str
    created_at: str = field(default_factory=lambda: datetime.datetime.now().strftime("%H:%M:%S"))
    status: str = "Pending"  # "Pending", "Assigned", "Completed"
    assigned_ambulance_id: Optional[str] = None
    assigned_strategy: Optional[str] = None
    simulated_travel_time: Optional[float] = None
    route: Optional[List[str]] = None

    @property
    def priority_rank(self) -> int:
        """Return numerical priority rank (1 = Critical ... 4 = Low)."""
        return PRIORITY_ORDER.get(self.priority, 99)

    @property
    def is_pending(self) -> bool:
        """Return True only if this incident is awaiting ambulance dispatch."""
        return self.status == "Pending"

    def assign_ambulance(
        self,
        ambulance_id: str,
        strategy: str,
        travel_time: float,
        route: List[str],
    ) -> None:
        """Commit an ambulance assignment to this incident."""
        if not self.is_pending:
            raise ValueError(f"Incident {self.id} is already {self.status}")
        self.status = "Assigned"
        self.assigned_ambulance_id = ambulance_id
        self.assigned_strategy = strategy
        self.simulated_travel_time = round(travel_time, 2)
        self.route = list(route)

    def mark_completed(self) -> None:
        """Mark incident resolved."""
        self.status = "Completed"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Incident:
        """Construct Incident from dictionary."""
        return cls(**data)


def validate_incident_input(
    location: str,
    priority: str,
    description: str,
    valid_nodes: List[str],
) -> Tuple[bool, Optional[str]]:
    """Validate user inputs when creating a synthetic emergency incident."""
    if not location or location not in valid_nodes:
        return False, f"Location '{location}' is not a valid node in the road network."
    if priority not in PRIORITY_ORDER:
        return False, f"Priority '{priority}' is invalid. Allowed: {list(PRIORITY_ORDER.keys())}"
    if not description or len(description.strip()) < 3:
        return False, "Description must be at least 3 characters long."
    return True, None


def generate_default_incidents() -> Dict[str, Incident]:
    """Generate realistic initial synthetic incidents for demonstration and testing."""
    incidents = [
        Incident(
            id="INC-100",
            location="INT_HARBOR_VIEW",
            priority="High",
            description="Simulated traffic collision near Harbor Promenade",
            created_at="17:20:10",
            status="Assigned",
            assigned_ambulance_id="AMB-04",
            assigned_strategy="Nearest Available",
            simulated_travel_time=2.2,
            route=["STA_BETA", "INT_HARBOR_VIEW"],
        ),
        Incident(
            id="INC-101",
            location="INT_DOWNTOWN",
            priority="Critical",
            description="Simulated acute cardiac emergency at Downtown Central Plaza",
            created_at="17:35:14",
            status="Pending",
        ),
        Incident(
            id="INC-102",
            location="INT_TECH_PARK",
            priority="High",
            description="Simulated industrial fall injury at Tech District Sector 4",
            created_at="17:38:22",
            status="Pending",
        ),
        Incident(
            id="INC-103",
            location="INT_UNIVERSITY",
            priority="Medium",
            description="Simulated sports field sprain at University Campus",
            created_at="17:40:05",
            status="Pending",
        ),
        Incident(
            id="INC-104",
            location="INT_OLD_TOWN",
            priority="Low",
            description="Simulated non-urgent patient transfer from Historic Old Town",
            created_at="17:41:50",
            status="Pending",
        ),
    ]
    return {inc.id: inc for inc in incidents}
