"""Scheduling domain types.

These types form the boundary between the scheduling use case, the solver
adapter, and persistence. They are independent of OR-Tools and the database.

The flow is:

    SchedulingSnapshot  (loaded domain rows)
        -> SchedulingProblem  (solver-ready minutes/edges/calendars)
        -> SolveResult  (raw solver output)
        -> Schedule  (validated, persistable result)

`SchedulingPolicy` carries the per-run knobs that are not part of the graph.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .enums import SolverStatus
from .errors import ValidationError
from .models import (
    FactoryHoliday,
    FactoryShift,
    Material,
    Operation,
    OperationDependency,
    OperationMaterial,
    Resource,
    WorkOrder,
)


@dataclass(frozen=True)
class SchedulingPolicy:
    """Per-run scheduling knobs."""

    horizon_days: int = 14
    time_limit_seconds: float = 60.0
    num_search_workers: int = 4
    random_seed: int = 0
    include_calendars: bool = False
    include_due_dates: bool = False

    def __post_init__(self) -> None:
        if self.horizon_days <= 0:
            raise ValidationError("Scheduling horizon_days must be greater than zero.")
        if self.time_limit_seconds <= 0:
            raise ValidationError(
                "Scheduling time_limit_seconds must be greater than zero."
            )
        if self.num_search_workers <= 0:
            raise ValidationError(
                "Scheduling num_search_workers must be greater than zero."
            )
        if self.random_seed < 0:
            raise ValidationError("Scheduling random_seed cannot be negative.")


@dataclass(frozen=True)
class SchedulingSnapshot:
    """A consistent read of all domain rows needed to build a schedule."""

    run_id: int
    operations: tuple[Operation, ...]
    resources: tuple[Resource, ...]
    work_orders: tuple[WorkOrder, ...]
    materials: tuple[Material, ...]
    dependencies: tuple[OperationDependency, ...]
    operation_materials: tuple[OperationMaterial, ...]
    shifts: tuple[FactoryShift, ...] = ()
    holidays: tuple[FactoryHoliday, ...] = ()

    def __post_init__(self) -> None:
        if self.run_id <= 0:
            raise ValidationError("SchedulingSnapshot run_id must be positive.")


@dataclass(frozen=True)
class SchedulingProblem:
    """Solver-ready graph expressed in relative minutes."""

    operations: tuple[Operation, ...]
    resources: tuple[Resource, ...]
    precedence: tuple[OperationDependency, ...]
    material_ready_minutes: Mapping[str, int]
    resource_blackouts: Mapping[str, tuple[tuple[int, int], ...]]
    horizon_minutes: int

    def __post_init__(self) -> None:
        if self.horizon_minutes <= 0:
            raise ValidationError("SchedulingProblem horizon_minutes must be positive.")
        for operation_id, ready_minute in self.material_ready_minutes.items():
            if ready_minute < 0:
                raise ValidationError(
                    f"Material ready minute for '{operation_id}' cannot be negative."
                )
        for resource_id, windows in self.resource_blackouts.items():
            for start, end in windows:
                if start < 0 or end <= start:
                    raise ValidationError(
                        f"Invalid blackout window for resource '{resource_id}': "
                        f"({start}, {end})."
                    )


@dataclass(frozen=True)
class Assignment:
    """One operation's optimized start/end offset in minutes."""

    operation_id: str
    start_minute: int
    end_minute: int
    resource_id: Optional[str] = None

    def __post_init__(self) -> None:
        if self.start_minute < 0:
            raise ValidationError("Assignment start_minute cannot be negative.")
        if self.end_minute <= self.start_minute:
            raise ValidationError("Assignment end_minute must be after start_minute.")


@dataclass(frozen=True)
class SolveResult:
    """Raw solver output before persistence."""

    status: SolverStatus
    assignments: tuple[Assignment, ...]
    objective_value: Optional[int] = None
    wall_time_seconds: Optional[float] = None

    def __post_init__(self) -> None:
        if self.objective_value is not None and self.objective_value < 0:
            raise ValidationError("SolveResult objective_value cannot be negative.")
        if self.wall_time_seconds is not None and self.wall_time_seconds < 0:
            raise ValidationError("SolveResult wall_time_seconds cannot be negative.")


@dataclass(frozen=True)
class Schedule:
    """A validated schedule ready for snapshot persistence."""

    run_id: int
    assignments: tuple[Assignment, ...]
    makespan_minutes: int
    planning_start: datetime
    solver_status: SolverStatus
    total_tardiness_minutes: int = 0

    def __post_init__(self) -> None:
        if self.run_id <= 0:
            raise ValidationError("Schedule run_id must be positive.")
        if self.makespan_minutes < 0:
            raise ValidationError("Schedule makespan_minutes cannot be negative.")
        if self.total_tardiness_minutes < 0:
            raise ValidationError("Schedule total_tardiness_minutes cannot be negative.")

    def assignment_for(self, operation_id: str) -> Optional[Assignment]:
        """Return the assignment for an operation, if present."""
        return next(
            (
                assignment
                for assignment in self.assignments
                if assignment.operation_id == operation_id
            ),
            None,
        )


# Re-exported for callers that build snapshots from a run record.
__all__ = [
    "SchedulingPolicy",
    "SchedulingSnapshot",
    "SchedulingProblem",
    "Assignment",
    "SolveResult",
    "Schedule",
]
