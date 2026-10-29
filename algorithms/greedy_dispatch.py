"""Greedy Emergency Dispatch Engine for MediRoute.

This module implements three algorithmic dispatch strategies:
1. Strategy A: Nearest Available Ambulance (Local Greedy Shortest Travel Time)
2. Strategy B: Priority-Aware Greedy Dispatch (Medical Urgency & Capability Awareness)
3. Strategy C: Greedy Batch Multi-Incident Dispatch (Iterative Priority-Ordered Assignment)

Algorithmic Paradigm:
- Greedy Heuristic: At each decision step, selects the locally optimal choice
  (minimal simulated travel time or highest capability match) with no backtracking.
- Important DAA Insight: Greedy dispatch solves single-incident matching optimally,
  but for multi-incident batch dispatch, greedy ordering does not guarantee a globally
  minimal aggregate response time (which would require Hungarian algorithm / Minimum-Cost
  Maximum Bipartite Matching). This trade-off is highlighted for student viva evaluation.
"""

from __future__ import annotations
import copy
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from algorithms.dijkstra import dijkstra_shortest_path
from graph.graph_utils import RoadNetwork
from simulation.ambulances import Ambulance
from simulation.incidents import Incident, PRIORITY_ORDER


@dataclass
class CandidateEvaluation:
    """Detailed evaluation of an individual ambulance candidate for an incident."""

    ambulance_id: str
    call_sign: str
    current_node: str
    status: str
    is_available: bool
    capability: str
    eligible: bool
    ineligibility_reason: Optional[str] = None
    path: List[str] = field(default_factory=list)
    travel_time: float = float("inf")
    explored_nodes: int = 0
    dijkstra_time_ms: float = 0.0
    rank: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DispatchResult:
    """Structured result returned by a single-incident dispatch evaluation."""

    incident_id: str
    incident_location: str
    incident_priority: str
    strategy: str
    selected_ambulance_id: Optional[str] = None
    selected_call_sign: Optional[str] = None
    route: List[str] = field(default_factory=list)
    estimated_travel_time: Optional[float] = None
    explored_nodes_total: int = 0
    computation_time_ms: float = 0.0
    status: str = "PENDING"  # "ASSIGNED", "NO_AVAILABLE_AMBULANCES", "UNREACHABLE", "ERROR"
    explanation: str = ""
    candidates: List[CandidateEvaluation] = field(default_factory=list)

    @property
    def is_successful(self) -> bool:
        return self.status == "ASSIGNED" and self.selected_ambulance_id is not None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.estimated_travel_time is not None:
            d["estimated_travel_time"] = round(self.estimated_travel_time, 2)
        d["computation_time_ms"] = round(self.computation_time_ms, 4)
        return d


@dataclass
class BatchDispatchResult:
    """Result of greedy batch processing across multiple pending incidents."""

    assignments: List[DispatchResult] = field(default_factory=list)
    unassigned_incidents: List[Tuple[str, str]] = field(default_factory=list)  # (incident_id, reason)
    total_travel_time: float = 0.0
    total_computation_time_ms: float = 0.0
    ambulances_assigned_count: int = 0
    strategy: str = "Greedy Batch Dispatch"
    explanation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy": self.strategy,
            "assignments_count": len(self.assignments),
            "unassigned_count": len(self.unassigned_incidents),
            "total_travel_time": round(self.total_travel_time, 2),
            "total_computation_time_ms": round(self.total_computation_time_ms, 4),
            "ambulances_assigned_count": self.ambulances_assigned_count,
            "assignments": [a.to_dict() for a in self.assignments],
            "unassigned_incidents": self.unassigned_incidents,
            "explanation": self.explanation,
        }


def evaluate_all_candidates(
    network: RoadNetwork,
    incident: Incident,
    ambulances: Dict[str, Ambulance],
) -> Tuple[List[CandidateEvaluation], int, float]:
    """Run Dijkstra from all ambulances to the incident location.

    Returns:
        A tuple of (candidate_evaluations, total_explored_nodes, total_dijkstra_ms).
    """
    candidates: List[CandidateEvaluation] = []
    total_explored = 0
    t_start = time.perf_counter()

    for amb_id in sorted(ambulances.keys()):
        amb = ambulances[amb_id]

        if not amb.is_available:
            candidates.append(
                CandidateEvaluation(
                    ambulance_id=amb.id,
                    call_sign=amb.call_sign,
                    current_node=amb.current_node,
                    status=amb.status,
                    is_available=False,
                    capability=amb.capability,
                    eligible=False,
                    ineligibility_reason=f"Vehicle is currently {amb.status}",
                )
            )
            continue

        # Run Dijkstra shortest path
        dijk_res = dijkstra_shortest_path(network.adjacency, amb.current_node, incident.location)
        total_explored += dijk_res.explored_nodes

        if not dijk_res.found:
            candidates.append(
                CandidateEvaluation(
                    ambulance_id=amb.id,
                    call_sign=amb.call_sign,
                    current_node=amb.current_node,
                    status=amb.status,
                    is_available=True,
                    capability=amb.capability,
                    eligible=False,
                    ineligibility_reason=f"No traversable road path to {incident.location}",
                    explored_nodes=dijk_res.explored_nodes,
                    dijkstra_time_ms=dijk_res.execution_time_ms,
                )
            )
        else:
            candidates.append(
                CandidateEvaluation(
                    ambulance_id=amb.id,
                    call_sign=amb.call_sign,
                    current_node=amb.current_node,
                    status=amb.status,
                    is_available=True,
                    capability=amb.capability,
                    eligible=True,
                    path=dijk_res.path,
                    travel_time=dijk_res.total_cost,
                    explored_nodes=dijk_res.explored_nodes,
                    dijkstra_time_ms=dijk_res.execution_time_ms,
                )
            )

    t_end = time.perf_counter()
    return candidates, total_explored, (t_end - t_start) * 1000.0


def nearest_available_dispatch(
    network: RoadNetwork,
    incident: Incident,
    ambulances: Dict[str, Ambulance],
) -> DispatchResult:
    """Strategy A: Select available ambulance with strictly minimal simulated travel time.

    Deterministic tie-breaking: Alphabetical order of ambulance ID.
    """
    candidates, total_explored, comp_time_ms = evaluate_all_candidates(network, incident, ambulances)

    eligible_candidates = [c for c in candidates if c.eligible]

    if not eligible_candidates:
        available_count = sum(1 for a in ambulances.values() if a.is_available)
        status = "NO_AVAILABLE_AMBULANCES" if available_count == 0 else "UNREACHABLE"
        reason = (
            "All simulated ambulances are currently busy."
            if available_count == 0
            else f"None of the {available_count} available ambulances can reach destination '{incident.location}'."
        )
        return DispatchResult(
            incident_id=incident.id,
            incident_location=incident.location,
            incident_priority=incident.priority,
            strategy="Nearest Available Ambulance",
            explored_nodes_total=total_explored,
            computation_time_ms=comp_time_ms,
            status=status,
            explanation=reason,
            candidates=candidates,
        )

    # Sort eligible candidates by travel_time ASC, then ambulance_id ASC (deterministic tie-breaking)
    eligible_candidates.sort(key=lambda c: (c.travel_time, c.ambulance_id))

    # Assign ranks to eligible candidates
    for idx, c in enumerate(eligible_candidates):
        c.rank = idx + 1

    best = eligible_candidates[0]
    explanation = (
        f"Selected {best.ambulance_id} ({best.call_sign}) because it has the minimum simulated travel time "
        f"({best.travel_time:.1f} min) across all {len(eligible_candidates)} eligible vehicles. "
        f"Route traverses {len(best.path)} nodes ({' -> '.join(best.path)})."
    )

    return DispatchResult(
        incident_id=incident.id,
        incident_location=incident.location,
        incident_priority=incident.priority,
        strategy="Nearest Available Ambulance",
        selected_ambulance_id=best.ambulance_id,
        selected_call_sign=best.call_sign,
        route=best.path,
        estimated_travel_time=best.travel_time,
        explored_nodes_total=total_explored,
        computation_time_ms=comp_time_ms,
        status="ASSIGNED",
        explanation=explanation,
        candidates=candidates,
    )


def priority_aware_dispatch(
    network: RoadNetwork,
    incident: Incident,
    ambulances: Dict[str, Ambulance],
) -> DispatchResult:
    """Strategy B: Priority-Aware Greedy Dispatch.

    Rules:
    - Critical (Urgency 1): Highest priority. If an Advanced Life Support (ALS) vehicle is reachable,
      it is strictly prioritized over Basic Life Support (BLS). Among ALS vehicles, choose minimum travel time.
      If no ALS is reachable, fall back to nearest BLS.
    - High / Medium / Low: Standard minimum travel time selection, with priority audit rationale.
    - Deterministic tie-breaking: Alphabetical by ambulance ID.
    """
    candidates, total_explored, comp_time_ms = evaluate_all_candidates(network, incident, ambulances)
    eligible = [c for c in candidates if c.eligible]

    if not eligible:
        available_count = sum(1 for a in ambulances.values() if a.is_available)
        status = "NO_AVAILABLE_AMBULANCES" if available_count == 0 else "UNREACHABLE"
        return DispatchResult(
            incident_id=incident.id,
            incident_location=incident.location,
            incident_priority=incident.priority,
            strategy="Priority-Aware Dispatch",
            explored_nodes_total=total_explored,
            computation_time_ms=comp_time_ms,
            status=status,
            explanation=f"Cannot dispatch for {incident.priority} incident: No eligible ambulances reachable.",
            candidates=candidates,
        )

    # Sort key depending on priority tier
    if incident.priority == "Critical":
        # ALS capability gets primary preference (0 for ALS, 1 for BLS), then travel_time, then ID
        eligible.sort(key=lambda c: (0 if c.capability == "ALS" else 1, c.travel_time, c.ambulance_id))
        als_available = any(c.capability == "ALS" for c in eligible)
        best = eligible[0]
        if als_available and best.capability == "ALS":
            explanation = (
                f"CRITICAL DISPATCH: Selected {best.ambulance_id} ({best.call_sign}) [ALS Capable] "
                f"with optimal response time of {best.travel_time:.1f} min. Priority protocol ensures "
                f"advanced resuscitation capability for life-threatening emergencies."
            )
        else:
            explanation = (
                f"CRITICAL DISPATCH (Degraded Capability): No ALS units reachable. Dispatched nearest BLS unit "
                f"{best.ambulance_id} ({best.call_sign}) with {best.travel_time:.1f} min response."
            )
    else:
        # High, Medium, Low: Standard minimum travel time
        eligible.sort(key=lambda c: (c.travel_time, c.ambulance_id))
        best = eligible[0]
        explanation = (
            f"{incident.priority.upper()} DISPATCH: Assigned nearest unit {best.ambulance_id} ({best.call_sign}) "
            f"with simulated travel time {best.travel_time:.1f} min."
        )

    for idx, c in enumerate(eligible):
        c.rank = idx + 1

    return DispatchResult(
        incident_id=incident.id,
        incident_location=incident.location,
        incident_priority=incident.priority,
        strategy="Priority-Aware Dispatch",
        selected_ambulance_id=best.ambulance_id,
        selected_call_sign=best.call_sign,
        route=best.path,
        estimated_travel_time=best.travel_time,
        explored_nodes_total=total_explored,
        computation_time_ms=comp_time_ms,
        status="ASSIGNED",
        explanation=explanation,
        candidates=candidates,
    )


def greedy_batch_dispatch(
    network: RoadNetwork,
    pending_incidents: List[Incident],
    ambulances: Dict[str, Ambulance],
) -> BatchDispatchResult:
    """Strategy C: Greedy Batch Multi-Incident Dispatch.

    Processes pending incidents sequentially according to strict priority order:
    Critical (1) > High (2) > Medium (3) > Low (4).
    For identical priorities, stable order by creation timestamp/ID.

    Important Constraint:
    - Each ambulance can be assigned AT MOST ONCE within the batch.
    - Operates on a local working copy of ambulance availability to preserve state purity.
    - Does NOT mutate the live simulation state.
    """
    t_start = time.perf_counter()

    # Sort incidents by priority rank ASC, then incident ID ASC
    sorted_incidents = sorted(
        pending_incidents,
        key=lambda inc: (inc.priority_rank, inc.id),
    )

    # Local working copies of ambulances
    working_ambulances: Dict[str, Ambulance] = copy.deepcopy(ambulances)

    assignments: List[DispatchResult] = []
    unassigned: List[Tuple[str, str]] = []
    total_travel_time = 0.0

    for inc in sorted_incidents:
        # Check if any ambulances are still available in our working set
        avail_count = sum(1 for a in working_ambulances.values() if a.is_available)
        if avail_count == 0:
            unassigned.append((inc.id, "Fleet exhausted (all simulated ambulances allocated in this batch)"))
            continue

        # Use Priority-Aware dispatch for each incident in the batch
        res = priority_aware_dispatch(network, inc, working_ambulances)

        if res.is_successful and res.selected_ambulance_id:
            assignments.append(res)
            total_travel_time += res.estimated_travel_time or 0.0
            # Mark ambulance as busy in our local working set
            amb = working_ambulances[res.selected_ambulance_id]
            amb.status = "Busy"
            amb.current_assigned_incident = inc.id
        else:
            unassigned.append((inc.id, res.explanation))

    t_end = time.perf_counter()
    comp_time_ms = (t_end - t_start) * 1000.0

    explanation = (
        f"Greedy Batch dispatched {len(assignments)} out of {len(sorted_incidents)} pending incidents "
        f"in {comp_time_ms:.2f} ms. Cumulative simulated travel time: {total_travel_time:.1f} min. "
        f"Incidents were evaluated in strict priority order (Critical -> High -> Medium -> Low). "
        f"Unassigned incidents: {len(unassigned)}."
    )

    return BatchDispatchResult(
        assignments=assignments,
        unassigned_incidents=unassigned,
        total_travel_time=total_travel_time,
        total_computation_time_ms=comp_time_ms,
        ambulances_assigned_count=len(assignments),
        strategy="Greedy Batch Dispatch",
        explanation=explanation,
    )
