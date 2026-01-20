Scheduler (high-level)
- Abstract Data Input
  - Class SchedulerDataInput
    - add variables
    - add domains (the value for variables)
- Pluggable Constraints
  - Class SchedulerConstraint
- Optional Objective
  - Class SchedulerObjective
    - Call SchedulerConstraint, SchedulerDataInput

- Class Scheduler
  - Flexible Model Builder
    - Class SchedulerModelBuilder
      - Call SchedulerObjective 
      - Extensible Output
      - Interface
      - Error Handling & Validation

#Abstract Data Input

Class: SchedulerDataInput
- init(self, data_source)
- add_variable(self, name, domain)
- get_variables(self)
- get_domains(self)
- validate_input(self)

#Pluggable Constraints

Class: SchedulerConstraint
- init(self)
- add_constraint(self, constraint_fn)
- apply_constraints(self, model, variables)

#Optional Objective

Class: SchedulerObjective
- init(self, objective_fn)
- set_objective(self, model, variables)

Class: Scheduler

- init(self, data_input, constraints, model_builder, objective=None)
- solve(self)
- get_output(self, format='dict')
- handle_errors(self)

#Flexible Model Builder

Class: SchedulerModelBuilder
- init(self, data_input, constraints, objective=None)
- build_model(self)
- set_output_handler(self, handler_fn)
- validate_model(self)

Scheduler (main entry point)
|- Receives: SchedulerDataInput, SchedulerConstraint, SchedulerModelBuilder, (optional) SchedulerObjective
|- Validates inputs
|- Calls SchedulerModelBuilder.build_model()
| |- Uses SchedulerDataInput to get variables/domains
| |- Applies SchedulerConstraint to add constraints to the model
| |- If SchedulerObjective is provided:
| | |- Calls SchedulerObjective.set_objective() to set the optimization goal
| |- Returns the built model
|- Calls solve() on the model
|- Collects and formats output (using output handler if set)
|- Returns solution or error

Details:
Scheduler
- what: The main orchestrator that coordinates data input, constraints, model building, and solving.
- why: Centralizes the scheduling process, ensuring all components interact correctly and results are returned in a consistent way.
- how: Receives inputs, validates them, calls the model builder, applies constraints and objectives, solves the model, and returns output or errors.

SchedulerDataInput
- what: Handles all scheduling data, including variables and their domains.
- why: Provides a flexible way to define and manage the data needed for scheduling, making the system adaptable to different use cases.
- how: Accepts data from various sources, allows adding variables and domains, validates input, and exposes data for model building.

SchedulerConstraint
- what: Encapsulates all rules and restrictions for the scheduling problem.
- why: Makes constraints modular and pluggable, so users can easily add, remove, or modify rules without changing core logic.
- how: Accepts constraint functions, applies them to the model and variables during model building.

SchedulerModelBuilder
- what: Builds the OR-Tools model using provided data, constraints, and (optionally) objectives.
- why: Separates model construction from orchestration, allowing for flexible and reusable model creation.
- how: Uses data input to create variables, applies constraints, sets objectives if present, validates the model, and prepares it for solving.

SchedulerObjective
- what: Defines the optimization goal for the scheduling problem (e.g., minimize time, maximize throughput).
- why: Allows users to specify what should be optimized, making the scheduler adaptable to different business needs.
- how: Accepts an objective function, applies it to the model and variables, and integrates with the model builder if provided.

---

**Example Problem:**  
Schedule 2 jobs on 1 machine.  
- Job A: duration 3  
- Job B: duration 2  
- Constraint: No overlap (machine can only do one job at a time)  
- Objective: Minimize makespan (total time to finish all jobs)

---

### 1. SchedulerDataInput

```python
class SchedulerDataInput:
    def __init__(self):
        self.variables = {}  # e.g., {'A': {'domain': (0, 10)}, ...}
        self.durations = {}  # e.g., {'A': 3, 'B': 2}

    def add_variable(self, name, domain, duration):
        self.variables[name] = {'domain': domain}
        self.durations[name] = duration

    def get_variables(self):
        return self.variables

    def get_durations(self):
        return self.durations
```

---

### 2. SchedulerConstraint

```python
class SchedulerConstraint:
    def __init__(self):
        self.constraints = []

    def add_constraint(self, constraint_fn):
        self.constraints.append(constraint_fn)

    def apply_constraints(self, model, variables, durations):
        for fn in self.constraints:
            fn(model, variables, durations)
```

Example constraint function:
```python
def no_overlap_constraint(model, variables, durations):
    # For all pairs, ensure no overlap
    jobs = list(variables.keys())
    for i in range(len(jobs)):
        for j in range(i+1, len(jobs)):
            a, b = jobs[i], jobs[j]
            model.Add(variables[a] + durations[a] <= variables[b]).OnlyEnforceIf(variables[a] <= variables[b])
            model.Add(variables[b] + durations[b] <= variables[a]).OnlyEnforceIf(variables[b] < variables[a])
```

---

### 3. SchedulerObjective

```python
class SchedulerObjective:
    def __init__(self, objective_fn):
        self.objective_fn = objective_fn

    def set_objective(self, model, variables, durations):
        self.objective_fn(model, variables, durations)
```

Example objective function:
```python
def minimize_makespan(model, variables, durations):
    makespan = model.NewIntVar(0, 100, 'makespan')
    for job in variables:
        model.Add(variables[job] + durations[job] <= makespan)
    model.Minimize(makespan)
```

---

### 4. SchedulerModelBuilder

```python
from ortools.sat.python import cp_model

class SchedulerModelBuilder:
    def __init__(self, data_input, constraints, objective=None):
        self.data_input = data_input
        self.constraints = constraints
        self.objective = objective

    def build_model(self):
        model = cp_model.CpModel()
        variables = {}
        durations = self.data_input.get_durations()
        for name, info in self.data_input.get_variables().items():
            domain = info['domain']
            variables[name] = model.NewIntVar(domain[0], domain[1], name)
        self.constraints.apply_constraints(model, variables, durations)
        if self.objective:
            self.objective.set_objective(model, variables, durations)
        return model, variables
```

---

### 5. Scheduler (Main)

```python
from ortools.sat.python import cp_model

class Scheduler:
    def __init__(self, data_input, constraints, model_builder, objective=None):
        self.data_input = data_input
        self.constraints = constraints
        self.model_builder = model_builder
        self.objective = objective

    def solve(self):
        model, variables = self.model_builder.build_model()
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return {name: solver.Value(var) for name, var in variables.items()}
        else:
            return None
```

---

### 6. Usage Example

```python
# 1. Prepare data input
data_input = SchedulerDataInput()
data_input.add_variable('A', (0, 10), 3)
data_input.add_variable('B', (0, 10), 2)

# 2. Prepare constraints
constraints = SchedulerConstraint()
constraints.add_constraint(no_overlap_constraint)

# 3. Prepare objective
objective = SchedulerObjective(minimize_makespan)

# 4. Prepare model builder
model_builder = SchedulerModelBuilder(data_input, constraints, objective)

# 5. Run scheduler
scheduler = Scheduler(data_input, constraints, model_builder, objective)
solution = scheduler.solve()
print(solution)  # e.g., {'A': 0, 'B': 3}
```

---

This pseudocode shows how each class is responsible for a part of the process, and how they interact to build and solve a modular scheduling problem with OR-Tools.