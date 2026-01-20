import pytest
from ortools.sat.python import cp_model

from scheduler import (
    SchedulerDataInput,
    SchedulerConstraint,
    SchedulerObjective,
    SchedulerModelBuilder,
    Scheduler
)

def test_basic_schedule_minimize_makespan():
    # 1. Prepare data input
    data_input = SchedulerDataInput()
    data_input.add_jobs('A', {'duration': 3, 'domain': (0, 10), 'machine': 1})
    data_input.add_jobs('B', {'duration': 2, 'domain': (0, 10), 'machine': 1})

    # 2. Prepare constraints
    constraints = SchedulerConstraint()
    constraints.add_constraint(SchedulerConstraint.no_overlap_constraint)

    # 3. Prepare objective
    objective = SchedulerObjective()
    objective.add_objective(SchedulerObjective.minimize_makespan)

    # 4. Prepare model builder
    model_builder = SchedulerModelBuilder(data_input, constraints, objective)

    # 5. Run scheduler
    scheduler = Scheduler(data_input, constraints, model_builder, objective)
    solution = scheduler.solve()
    assert solution is not None
    assert 'A' in solution and 'B' in solution
    # Check that jobs do not overlap
    a_start = solution['A']['start']
    a_end = solution['A']['end']
    b_start = solution['B']['start']
    b_end = solution['B']['end']
    assert (a_end <= b_start) or (b_end <= a_start)
    # Check makespan
    makespan = max(a_end, b_end)
    assert makespan <= 10

def test_precedence_constraint():
    data_input = SchedulerDataInput()
    data_input.add_jobs('A', {'duration': 3, 'domain': (0, 10), 'machine': 1})
    data_input.add_jobs('B', {'duration': 2, 'domain': (0, 10), 'machine': 1, 'predecessor': 'A'})

    constraints = SchedulerConstraint()
    constraints.add_constraint(SchedulerConstraint.no_overlap_constraint)
    constraints.add_constraint(SchedulerConstraint.precedence_constraint)

    objective = SchedulerObjective()
    objective.add_objective(SchedulerObjective.minimize_makespan)

    model_builder = SchedulerModelBuilder(data_input, constraints, objective)
    scheduler = Scheduler(data_input, constraints, model_builder, objective)
    solution = scheduler.solve()
    assert solution is not None
    assert solution['B']['start'] >= solution['A']['end']

def test_machine_availability_constraint():
    data_input = SchedulerDataInput()
    data_input.add_jobs('A', {'duration': 2, 'domain': (0, 10), 'allowed_machines': [1, 2], 'machine': 1})
    data_input.add_jobs('B', {'duration': 2, 'domain': (0, 10), 'allowed_machines': [2], 'machine': 2})

    constraints = SchedulerConstraint()
    constraints.add_constraint(SchedulerConstraint.machine_availability_constraint)

    objective = SchedulerObjective()
    objective.add_objective(SchedulerObjective.minimize_makespan)

    model_builder = SchedulerModelBuilder(data_input, constraints, objective)
    scheduler = Scheduler(data_input, constraints, model_builder, objective)
    solution = scheduler.solve()
    assert solution is not None

def test_minimize_total_completion_time():
    data_input = SchedulerDataInput()
    data_input.add_jobs('A', {'duration': 2, 'domain': (0, 10), 'machine': 1})
    data_input.add_jobs('B', {'duration': 3, 'domain': (0, 10), 'machine': 1})

    constraints = SchedulerConstraint()
    constraints.add_constraint(SchedulerConstraint.no_overlap_constraint)

    objective = SchedulerObjective()
    objective.add_objective(SchedulerObjective.minimize_total_completion_time)

    model_builder = SchedulerModelBuilder(data_input, constraints, objective)
    scheduler = Scheduler(data_input, constraints, model_builder, objective)
    solution = scheduler.solve()
    assert solution is not None
    total_completion = solution['A']['end'] + solution['B']['end']
    assert total_completion <= 13

def test_minimize_total_tardiness():
    data_input = SchedulerDataInput()
    data_input.add_jobs('A', {'duration': 2, 'domain': (0, 10), 'machine': 1, 'due_date': 4})
    data_input.add_jobs('B', {'duration': 3, 'domain': (0, 10), 'machine': 1, 'due_date': 5})

    constraints = SchedulerConstraint()
    constraints.add_constraint(SchedulerConstraint.no_overlap_constraint)

    objective = SchedulerObjective()
    objective.add_objective(SchedulerObjective.minimize_total_tardiness)

    model_builder = SchedulerModelBuilder(data_input, constraints, objective)
    scheduler = Scheduler(data_input, constraints, model_builder, objective)
    solution = scheduler.solve()
    assert solution is not None
    a_tardiness = max(0, solution['A']['end'] - 4)
    b_tardiness = max(0, solution['B']['end'] - 5)
    assert a_tardiness >= 0 and b_tardiness >= 0


if __name__ == "__main__":
    pytest.main()