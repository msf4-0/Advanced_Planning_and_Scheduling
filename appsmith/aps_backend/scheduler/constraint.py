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

    # Built-in constraints (User can add more)
    # once function is added here with @staticmethod, user can register it via add_constraint
   
    @staticmethod
    def no_overlap_constraint(model, job_vars, jobs):
        """
        Ensure no two jobs assigned to the same machine overlap in time.
        """
        # Collect intervals for each machine
        machine_to_intervals = {}
        for job, props in jobs.items():
            machine = props.get('machine')
            if machine is not None:
                if machine not in machine_to_intervals:
                    machine_to_intervals[machine] = []
                machine_to_intervals[machine].append(job_vars[job]['interval'])
        for intervals in machine_to_intervals.values():
            if len(intervals) > 1:
                model.AddNoOverlap(intervals)

    @staticmethod
    def precedence_constraint(model, job_vars, jobs):
        """
        Ensure that if a job has a 'predecessor', it starts after the predecessor ends.
        """
        for job, props in jobs.items():
            pred = props.get('predecessor')
            if pred and pred in job_vars:
                model.Add(job_vars[job]['start'] >= job_vars[pred]['end'])

