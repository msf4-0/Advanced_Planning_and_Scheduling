"""
Scheduler objectives module for job scheduling using OR-Tools.
Defines various objective functions that can be applied to the scheduling model.
Designed to work with SchedulerDataInput and SchedulerConstraint.
"""



from ortools.sat.python import cp_model
from typing import Callable, List, Dict

class SchedulerObjective:
    """
    Class to manage and apply objectives for the scheduler using OR-Tools.
    Supports registering multiple objectives and applying them to the model.
    Designed to synergize with SchedulerConstraint and SchedulerDataInput.
    """

    def __init__(self):
        """
        Initialize the SchedulerObjective with empty objectives list.
        
        """
        self.objectives: List[Callable[[cp_model.CpModel, Dict, Dict], cp_model.IntVar]] = []
        self.weights: List[float] = []

    def add_objective(self, objective_fn: Callable[[cp_model.CpModel, Dict, Dict], cp_model.IntVar], weight: float = 1.0):
        """
        Register an objective function with an optional weight.
        :param objective_fn: Function with signature (model, job_vars, jobs) -> IntVar
        :param weight: Weight for this objective in the combined objective function
        """
        self.objectives.append(objective_fn)
        self.weights.append(weight)

    def apply_objectives(self, model: cp_model.CpModel, job_vars: dict, jobs: dict):
        """
        Apply all registered objectives to the model as a weighted sum.
        :param model: OR-Tools CpModel
        :param job_vars: Dict of job variables (e.g., start, end, interval)
        :param jobs: Dict of job properties
        """
        if not self.objectives:
            return  # No objectives to apply

        # Compute weighted sum of objectives
        objective_vars = []
        for fn, w in zip(self.objectives, self.weights):
            obj_var = fn(model, job_vars, jobs)
            if w != 1.0:
                weighted_var = model.NewIntVar(0, int(1e9), f'weighted_obj_{len(objective_vars)}')
                model.AddMultiplicationEquality(weighted_var, [obj_var, int(w)])
                objective_vars.append(weighted_var)
            else:
                objective_vars.append(obj_var)
        
        if len(objective_vars) == 1:
            model.Minimize(objective_vars[0])
        else:
            model.Minimize(sum(objective_vars))

    