"""Ports for the scheduling use case.

The high-level scheduling policy depends on these protocols, not on psycopg,
OR-Tools, or FastAPI. Adapters in `app/adapters/` implement them.
"""

from typing import Protocol

from app.domain.scheduling import (
    Schedule,
    SchedulingPolicy,
    SchedulingProblem,
    SchedulingSnapshot,
    SolveResult,
)


class ScheduleDataPort(Protocol):
    """Loads a consistent domain snapshot for a run."""

    def load(self, run_id: int, policy: SchedulingPolicy) -> SchedulingSnapshot:
        """Return all operations, resources, materials, and constraints."""
        ...


class SolverPort(Protocol):
    """Solves a scheduling problem."""

    def solve(
        self,
        problem: SchedulingProblem,
        policy: SchedulingPolicy,
    ) -> SolveResult:
        """Return the raw solver result; never persist from an adapter."""
        ...


class ScheduleStorePort(Protocol):
    """Persists a completed schedule in one transaction."""

    def persist(self, run_id: int, schedule: Schedule) -> None:
        """Write allocations, statuses, and run metrics atomically."""
        ...


class RunLogPort(Protocol):
    """Creates and closes scheduling run audit records."""

    def start(self, message: str = "") -> int:
        """Create a run and return its identifier."""
        ...

    def finish(self, run_id: int, message: str) -> None:
        """Mark a run successful with a summary message."""
        ...

    def fail(self, run_id: int, error: str) -> None:
        """Mark a run failed and record the error."""
        ...


__all__ = [
    "ScheduleDataPort",
    "SolverPort",
    "ScheduleStorePort",
    "RunLogPort",
]
