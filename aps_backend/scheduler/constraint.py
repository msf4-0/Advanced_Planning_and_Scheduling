"""
Scheduler constraints module for job scheduling using OR-Tools.
Defines various constraints that can be applied to the scheduling model.
Designed to work with SchedulerDataInput and SchedulerObjective.
"""

import logging
from ortools.sat.python import cp_model
from typing import Callable

class SchedulerConstraint:
    """
    Class to manage and apply constraints for the scheduler.
    Constraints are functions that take (model, job_vars, jobs) and add rules to the model.
    """
    def __init__(self):
        self.constraints = []
        self.add_constraint(self.precedence_constraint)
        self.add_constraint(self.no_overlap_constraint)

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

    def precedence_constraint(self, model: cp_model.CpModel, job_vars: dict, jobs: dict):
        """
        Enforce sequencing: if a job (or product block) has a 'predecessor', it must start after the predecessor ends.
        Uses the dynamic key for 'predecessor' from config.json fields mapping.
        """
        pred_key = 'predecessor'  # This can be made dynamic if needed
        for job, props in jobs.items():
            pred = props.get(pred_key)
            if pred and pred in job_vars:
                model.Add(job_vars[job]['start'] >= job_vars[pred]['end'])
            else:
                logging.warning(f"Job {job} has no predecessor assigned or predecessor not in job_vars; skipping precedence constraint.")

    def no_overlap_constraint(self, model: cp_model.CpModel, job_vars: dict, jobs: dict):
        """
        Ensure no two jobs assigned to the same resources overlap in time.
        Uses the dynamic key for 'resources' from config.json fields mapping.
        """
        resources_key = 'resources'
        resources_to_intervals = {}
        for job, props in jobs.items():
            resources = props.get(resources_key)
            if resources is not None:
                if resources not in resources_to_intervals:
                    resources_to_intervals[resources] = []
                resources_to_intervals[resources].append(job_vars[job]['interval'])
            else:
                logging.warning(f"Job {job} has no resources assigned; skipping no-overlap constraint.")
        for intervals in resources_to_intervals.values():
            if len(intervals) > 1:
                model.AddNoOverlap(intervals)