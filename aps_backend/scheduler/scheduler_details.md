## Scheduler internals (matches current code)

This folder implements a small, modular OR-Tools CP-SAT scheduler. The backend pipeline (see `aps_backend/main.py`) builds job dictionaries from DB/graph ingestion, feeds them into these classes, and returns a per-job result dictionary.

### Modules & responsibilities

- `dataInput.py` – holds normalized input (`jobs`) and solved output (`values`).
- `modelBuilder.py` – creates OR-Tools variables (default: start/end/interval/resources) and wires constraints + objectives.
- `constraint.py` – pluggable constraints (default: precedence + no-overlap).
- `objective.py` – pluggable objectives (default: makespan + total completion time).
- `scheduler.py` – solves the model and writes solved values back to `SchedulerDataInput`.

---

# 1) SchedulerDataInput (`dataInput.py`)

`SchedulerDataInput` is the container used by the scheduler. It stores:

- `jobs: dict[str, dict]` – the input job definitions.
- `values: dict[str, dict]` – results for each job after solve.

### Key methods

- `add_jobs(name: str, properties: dict) -> None`
- `store_result(name: str, results: dict) -> None`
- `get_job_properties(name: str) -> dict`
- `get_value(name: str) -> dict`
- `validate_input() -> bool` (currently only checks that `jobs` is non-empty)

### Expected job properties (current defaults)

The default model builder and constraints expect these keys (all optional, but you’ll get a weaker model if you omit them):

- `duration` (int, default `1`)
- `domain` (tuple `(start_min, start_max)`, default `(0, 1000)`)
- `allowed_resources` (list[int], default `[1]`) – allowed machine/resource IDs
- `predecessor` (str, optional) – name of predecessor job

---

# 2) SchedulerModelBuilder (`modelBuilder.py`)

`SchedulerModelBuilder.build_model()` creates an OR-Tools `CpModel`, builds job variables, then applies constraints and objectives:

1. `job_vars = create_job_vars_default(model, data_input.jobs)`
2. `constraints.apply_constraints(model, job_vars, data_input.jobs)`
3. `objective.apply_objectives(model, job_vars, data_input.jobs)` (if provided)

### Default decision variables per job

Created by `create_job_vars_default(...)`:

- `start`: `IntVar` in `[domain[0], domain[1]]`
- `end`: `IntVar` in `[domain[0], domain[1]]`
- `interval`: `IntervalVar(start, duration, end)`
- `resources`: `IntVar` with domain from `allowed_resources`
- `duration`: stored as a Python int (not an OR-Tools variable)

So `job_vars[job_name]` looks like:

```python
{
  "start": <IntVar>,
  "end": <IntVar>,
  "interval": <IntervalVar>,
  "duration": 6,
  "resources": <IntVar>,
}
```

### Extending variable creation

If you need additional variables (setup times, alternative machines, batching, etc.), add another `create_job_vars_*` method and call it from `build_model()` instead of `create_job_vars_default`.

---

# 3) SchedulerConstraint (`constraint.py`)

Constraints are functions with the signature:

```python
(model: cp_model.CpModel, job_vars: dict, jobs: dict) -> None
```

`SchedulerConstraint` registers two constraints by default:

## a) Precedence constraint

If a job has `predecessor` and that predecessor exists in the model, enforce:

$$start(job) \ge end(predecessor)$$

Input requirement: `jobs[job_name]["predecessor"]` should be the *name* of another job.

## b) No-overlap constraint (current behavior)

The implementation groups intervals by `jobs[job_name]["resources"]` and applies `AddNoOverlap(...)` within each group.

Important caveat:

- The default model creates a *decision variable* `job_vars[job_name]["resources"]` from `allowed_resources`.
- The current no-overlap constraint does **not** use that decision variable; it looks for a fixed `resources` value inside the job properties.

Practical implications:

- If you **don’t** provide `resources` in the input job properties, the constraint logs warnings and effectively does nothing.
- If you **do** provide a fixed `resources` value per job (pre-assigned machine), then it will enforce no-overlap for jobs on the same resource.

---

# 4) SchedulerObjective (`objective.py`)

Objectives are functions with the signature:

```python
(model: cp_model.CpModel, job_vars: dict, jobs: dict) -> cp_model.IntVar
```

`SchedulerObjective` registers two objectives by default:

- `minimize_makespan`: minimize max of all `end` variables
- `minimize_total_completion_time`: minimize sum of all `end` variables

`apply_objectives(...)` combines them as a weighted sum.

Note on weights: the current implementation multiplies objectives by `int(weight)`, so non-integer weights will be truncated.

---

# 5) Scheduler (`scheduler.py`)

`Scheduler.solve(solver_params=None)` builds the model via the model builder and runs OR-Tools `CpSolver`.

### Solver parameters

You can pass CP-SAT parameters as a dictionary (they are set via `setattr(solver.parameters, param, value)`), for example:

```python
solver_params = {
  "max_time_in_seconds": 10,
  "num_search_workers": 8,
}
```

### Output format

If the solve is `FEASIBLE` or `OPTIMAL`, the scheduler stores results into `data_input.values` and returns it.

- Only `IntVar` values are exported.
- `IntervalVar` is not exported.
- The stored `duration` (Python int) is not exported.

So the returned structure is typically:

```python
{
  "JOB_A": {"start": 0, "end": 6, "resources": 2},
  "JOB_B": {"start": 6, "end": 10, "resources": 2},
}
```

If the model is infeasible, it returns `None`.

---

# Minimal example (matches current APIs)

```python
from aps_backend.scheduler.dataInput import SchedulerDataInput
from aps_backend.scheduler.constraint import SchedulerConstraint
from aps_backend.scheduler.objective import SchedulerObjective
from aps_backend.scheduler.modelBuilder import SchedulerModelBuilder
from aps_backend.scheduler.scheduler import Scheduler

data = SchedulerDataInput()

data.add_jobs("A", {
    "duration": 3,
    "domain": (0, 10),
    "allowed_resources": [1],
    "resources": 1,  # required for current no-overlap behavior
})
data.add_jobs("B", {
    "duration": 2,
    "domain": (0, 10),
    "allowed_resources": [1],
    "resources": 1,
    "predecessor": "A",
})

constraints = SchedulerConstraint()
objective = SchedulerObjective()
builder = SchedulerModelBuilder(data, constraints, objective)
scheduler = Scheduler(data, constraints, builder, objective)

result = scheduler.solve({"max_time_in_seconds": 5})
print(result)
```


This pseudocode shows how each class is responsible for a part of the process, and how they interact to build and solve a modular scheduling problem with OR-Tools.