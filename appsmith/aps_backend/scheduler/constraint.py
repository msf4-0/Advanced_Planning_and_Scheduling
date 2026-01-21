"""
Scheduler constraints module for job scheduling using OR-Tools.
Defines various constraints that can be applied to the scheduling model.
Designed to work with SchedulerDataInput and SchedulerObjective.

Create custom constraints by adding static methods and registering them via add_constraint. (If added inside the class then use @staticmethod decorator.)
Example:
    constraint = SchedulerConstraint()
    constraint.add_constraint(SchedulerConstraint.no_overlap_constraint)
    constraint.add_constraint(SchedulerConstraint.<your_custom_constraint>)


Template for constraint functions:

    @staticmethod # Add @staticmethod decorator if inside the class else omit it
    def your_custom_constraint(model: cp_model.CpModel, job_vars: dict, jobs: dict):
        '''
        Describe what this constraint does.
        Example: "Ensure job X starts after job Y ends."
        '''
        for job, props in jobs.items():
            # Example: Only apply to jobs with a certain property
            if props.get('some_property') == 'some_value':
                # Add your constraint logic here
                # Example: model.Add(job_vars[job]['start'] >= 10)
                pass  # Replace with your logic
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

    # Built-in constraints (User can add more)
    # once function is added here with @staticmethod, user can register it via add_constraint

    @staticmethod
    def no_overlap_constraint(model: cp_model.CpModel, job_vars: dict, jobs: dict):
        """
        Ensure no two jobs assigned to the same machine overlap in time.
        property key in config: 'machine'
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
    def precedence_constraint(model: cp_model.CpModel, job_vars: dict, jobs: dict):
        """
        Ensure that if a job has a 'predecessor', it starts after the predecessor ends.
        property key in config: 'predecessor'
        """
        for job, props in jobs.items():
            pred = props.get('predecessor')
            if pred and pred in job_vars:
                model.Add(job_vars[job]['start'] >= job_vars[pred]['end'])

    @staticmethod
    def machine_availability_constraint(model: cp_model.CpModel, job_vars: dict, jobs: dict):
        """
        Ensure that jobs are only scheduled on their allowed machines.
        property key in config: 'allowed_machines' (list of machine IDs)
        """
        for job, props in jobs.items():
            allowed_machines = props.get('allowed_machines')
            if allowed_machines is not None:
                machine_var = model.NewIntVarFromDomain(
                    cp_model.Domain.FromValues(allowed_machines),
                    f"{job}_machine"
                )
                # Assuming job_vars has a 'machine' variable
                model.Add(job_vars[job]['machine'] == machine_var)