"""
Scheduler constraints module for job scheduling using OR-Tools.
Defines various constraints that can be applied to the scheduling model.
Designed to work with SchedulerDataInput and SchedulerObjective.
"""

from ortools.sat.python import cp_model
from typing import Callable

class SchedulerConstraint:
    """
    Class to manage and apply constraints for the scheduler.
    Constraints are functions that take (model, job_vars, jobs) and add rules to the model.
    """
    def __init__(self):
        self.constraints = []

    def add_constraint(self, constraint_fn: Callable[[cp_model.CpModel, dict, dict], None]):
        """
        Add a constraint function to the list.
        :param constraint_fn: Function with signature (model, job_vars, jobs)
        """
        self.constraints.append(constraint_fn)

    def apply_constraints(self, model: cp_model.CpModel, job_vars: dict, jobs: dict):
        """
        Apply all registered constraints to the model.
        :param model: OR-Tools CpModel
        :param job_vars: Dict of job variables (e.g., start, end, interval)
        :param jobs: Dict of job properties
        """
        for fn in self.constraints:
            fn(model, job_vars, jobs)
