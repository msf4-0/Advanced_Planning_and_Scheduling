"""
Scheduler objectives module for job scheduling using OR-Tools.
Defines various objective functions that can be applied to the scheduling model.
Designed to work with SchedulerDataInput and SchedulerConstraint.

Create custom objectives by adding static methods and registering them via add_objective.
Example:
    objective = SchedulerObjective()
    objective.add_objective(SchedulerObjective.minimize_makespan)
    objective.add_objective(SchedulerObjective.<your_custom_objective>)


Template for objective functions:

    @staticmethod # Add @staticmethod decorator if inside the class else omit it
    def your_custom_objective(model: cp_model.CpModel, job_vars: dict, jobs: dict):
        '''
        Describe what this objective does.
        Example: "Minimize total tardiness of all jobs."
        '''
        # Define and return an IntVar representing the objective
        objective_var = model.NewIntVar(0, int(1e9), 'your_objective_name')
        # Add constraints to define objective_var based on job_vars and jobs
        return objective_var
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

    # Built-in objectives

    @staticmethod
    def minimize_makespan(model: cp_model.CpModel, job_vars: dict, jobs: dict):
        """
        Objective: Minimize the makespan (maximum job end time).
        """
        end_vars = [job_vars[job]['end'] for job in jobs]
        makespan = model.NewIntVar(0, int(1e9), 'makespan')
        model.AddMaxEquality(makespan, end_vars)
        return makespan

    @staticmethod
    def minimize_total_completion_time(model: cp_model.CpModel, job_vars: dict, jobs: dict):
        """
        Objective: Minimize the sum of all job end times.
        """
        end_vars = [job_vars[job]['end'] for job in jobs]
        total_completion = model.NewIntVar(0, int(1e9), 'total_completion')
        model.Add(total_completion == sum(end_vars))
        return total_completion

    @staticmethod
    def minimize_total_tardiness(model: cp_model.CpModel, job_vars: dict, jobs: dict):
        """
        Objective: Minimize total tardiness (lateness beyond due date).
        Assumes each job has a 'due_date' property.
        """
        tardiness_vars = []
        for job, props in jobs.items():
            due = props.get('due_date', 0)
            end = job_vars[job]['end']
            tardiness = model.NewIntVar(0, int(1e9), f'tardiness_{job}')
            model.Add(tardiness >= end - due)
            model.Add(tardiness >= 0)
            tardiness_vars.append(tardiness)
        total_tardiness = model.NewIntVar(0, int(1e9), 'total_tardiness')
        model.Add(total_tardiness == sum(tardiness_vars))
        return total_tardiness
    
    @staticmethod
    def minimize_total_deviation_from_planned(model: cp_model.CpModel, job_vars: dict, jobs: dict):
        """
        Objective: Minimize the total deviation from planned quantity (P vs A) for all jobs/blocks.
        Assumes each job has a 'qty_ordered' property and job_vars[job]['qty_initialized'] variable.
        If qty_initialized is not a variable, you may need to adapt this to your model.
        """
        deviation_vars = []
        for job, props in jobs.items():
            planned = props.get('qty_ordered', 0)
            # If qty_initialized is a variable in your model, use it; otherwise, use duration or another proxy
            actual = job_vars[job].get('qty_initialized', None)
            if actual is None:
                # Fallback: use duration as proxy for produced quantity
                actual = job_vars[job]['duration'] if 'duration' in job_vars[job] else None
            else:
                diff = model.NewIntVar(0, int(1e9), f'deviation_{job}')
                model.Add(diff == abs(planned - actual))
                deviation_vars.append(diff)
        total_deviation = model.NewIntVar(0, int(1e9), 'total_deviation')
        if deviation_vars:
            model.Add(total_deviation == sum(deviation_vars))
        else:
            model.Add(total_deviation == 0)
        return total_deviation