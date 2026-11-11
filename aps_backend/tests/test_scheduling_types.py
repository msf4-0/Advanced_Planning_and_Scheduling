"""Tests for the scheduling domain boundary types."""

from dataclasses import FrozenInstanceError
from datetime import date, datetime, time

import pytest

from app.domain.enums import SolverStatus
from app.domain.errors import ValidationError
from app.domain.models import (
    FactoryHoliday,
    FactoryShift,
    Material,
    Operation,
    OperationDependency,
    OperationMaterial,
    Resource,
    WorkOrder,
)
from app.domain.scheduling import (
    Assignment,
    Schedule,
    SchedulingPolicy,
    SchedulingProblem,
    SchedulingSnapshot,
    SolveResult,
)


def _sample_snapshot() -> SchedulingSnapshot:
    return SchedulingSnapshot(
        run_id=1,
        operations=(
            Operation(
                id="OP-1",
                work_order_id="WO-1",
                sequence_number=10,
                duration_minutes=45,
            ),
        ),
        resources=(Resource(id="MCH-1", name="Mill"),),
        work_orders=(
            WorkOrder(
                id="WO-1",
                target_item_id="ITEM-1",
                quantity_to_make=10,
                due_date=datetime(2026, 1, 1, 8, 0),
            ),
        ),
        materials=(Material(id="MAT-1", name="Steel"),),
        dependencies=(
            OperationDependency(upstream_op_id="OP-1", downstream_op_id="OP-2"),
        ),
        operation_materials=(
            OperationMaterial(
                operation_id="OP-1",
                material_id="MAT-1",
                quantity_required=1.0,
            ),
        ),
        shifts=(
            FactoryShift(
                resource_id="MCH-1",
                day_of_week=1,
                start_time=time(8, 0),
                end_time=time(17, 0),
            ),
        ),
        holidays=(FactoryHoliday(holiday_date=date(2026, 1, 1)),),
    )


def test_policy_defaults_and_validation():
    policy = SchedulingPolicy()
    assert policy.horizon_days == 14
    assert policy.num_search_workers == 4

    with pytest.raises(ValidationError, match="horizon_days"):
        SchedulingPolicy(horizon_days=0)
    with pytest.raises(ValidationError, match="time_limit_seconds"):
        SchedulingPolicy(time_limit_seconds=0)
    with pytest.raises(ValidationError, match="num_search_workers"):
        SchedulingPolicy(num_search_workers=0)


def test_snapshot_preserves_loaded_entities():
    snapshot = _sample_snapshot()

    assert snapshot.run_id == 1
    assert snapshot.operations[0].id == "OP-1"
    assert snapshot.shifts[0].resource_id == "MCH-1"
    assert snapshot.holidays[0].holiday_date == date(2026, 1, 1)


def test_problem_holds_solver_inputs_and_validates_minutes():
    problem = SchedulingProblem(
        operations=_sample_snapshot().operations,
        resources=_sample_snapshot().resources,
        precedence=_sample_snapshot().dependencies,
        material_ready_minutes={"OP-1": 120},
        resource_blackouts={"MCH-1": ((0, 30),)},
        horizon_minutes=20160,
    )

    assert problem.material_ready_minutes["OP-1"] == 120
    assert problem.resource_blackouts["MCH-1"] == ((0, 30),)

    with pytest.raises(ValidationError, match="horizon_minutes"):
        SchedulingProblem(
            operations=(),
            resources=(),
            precedence=(),
            material_ready_minutes={},
            resource_blackouts={},
            horizon_minutes=0,
        )
    with pytest.raises(ValidationError, match="ready minute"):
        SchedulingProblem(
            operations=(),
            resources=(),
            precedence=(),
            material_ready_minutes={"OP-1": -1},
            resource_blackouts={},
            horizon_minutes=60,
        )
    with pytest.raises(ValidationError, match="blackout window"):
        SchedulingProblem(
            operations=(),
            resources=(),
            precedence=(),
            material_ready_minutes={},
            resource_blackouts={"MCH-1": ((30, 30),)},
            horizon_minutes=60,
        )


def test_assignment_schedule_and_solver_result():
    assignment = Assignment(
        operation_id="OP-1",
        start_minute=0,
        end_minute=45,
        resource_id="MCH-1",
    )
    solve_result = SolveResult(
        status=SolverStatus.OPTIMAL,
        assignments=(assignment,),
        objective_value=45,
        wall_time_seconds=0.2,
    )
    schedule = Schedule(
        run_id=1,
        assignments=(assignment,),
        makespan_minutes=45,
        planning_start=datetime(2026, 1, 1, 8, 0),
        solver_status=SolverStatus.OPTIMAL,
    )

    assert solve_result.assignments[0].end_minute == 45
    assert schedule.assignment_for("OP-1") is assignment
    assert schedule.assignment_for("MISSING") is None

    with pytest.raises(ValidationError, match="end_minute"):
        Assignment(operation_id="OP-1", start_minute=10, end_minute=10)
    with pytest.raises(ValidationError, match="makespan_minutes"):
        Schedule(
            run_id=1,
            assignments=(),
            makespan_minutes=-1,
            planning_start=datetime(2026, 1, 1),
            solver_status=SolverStatus.OPTIMAL,
        )


def test_scheduling_types_are_frozen():
    policy = SchedulingPolicy()

    with pytest.raises(FrozenInstanceError):
        policy.horizon_days = 2
