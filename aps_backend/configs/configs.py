from ortools.sat.python import cp_model
from typing import Callable
from scheduler import SchedulerConstraint, SchedulerObjective
from .baseConfigs import *
import logging


class Configs:
    """
    Create custom constraints by adding static methods and registering them via add_constraint.
    Example:
        constraint = SchedulerConstraint()
        constraint.add_constraint(SchedulerConstraint.no_overlap_constraint)
        constraint.add_constraint(SchedulerConstraint.<your_custom_constraint>)

    Template for constraint functions:

    def your_custom_constraint(self, model: cp_model.CpModel, job_vars: dict, jobs: dict):
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
                
    Similarly, create custom objectives by adding static methods and registering them via add_objective.
    Template for objective functions:

    def your_custom_objective(self, model: cp_model.CpModel, job_vars: dict, jobs: dict):
        '''
        Describe what this objective does.
        Example: "Minimize total tardiness of all jobs."
        '''
        # Define and return an IntVar representing the objective
        objective_var = model.NewIntVar(0, int(1e9), 'your_objective_name')
        # Add constraints to define objective_var based on job_vars and jobs
        return objective_var
    """
    def __init__(self, constraintClass: SchedulerConstraint, objectiveClass: SchedulerObjective, mapping: dict):
        """
        mapping: should be the config dict from SchemaMapper (config.json)
        """
        self.constraintClass = constraintClass
        self.objectiveClass = objectiveClass
        self.mapping = mapping

        # Extract job fields mapping for dynamic property access
        self.job_fields = self.mapping.get('job_mapping', {}).get('fields', {})
        # You can add similar lines for machines/materials if needed

        self.constraintClass.add_constraint(self.precedence_constraint)
        self.constraintClass.add_constraint(self.no_overlap_constraint)
        self.constraintClass.add_constraint(self.machine_availability_constraint)
        # self.constraintClass.add_constraint(self.machine_downtime_constraint)
        # self.constraintClass.add_constraint(self.lock_sequence_constraint)

        self.objectiveClass.add_objective(self.minimize_makespan)
        self.objectiveClass.add_objective(self.minimize_total_tardiness)
        self.objectiveClass.add_objective(self.minimize_total_completion_time)



    # --------------- CONSTRAINTS ---------------
    # Built-in constraints (User can add more)
    # once function is added here with , user can register it via add_constraint

    
    def no_overlap_constraint(self, model: cp_model.CpModel, job_vars: dict, jobs: dict):
        """
        Ensure no two jobs assigned to the same machine overlap in time.
        Uses the dynamic key for 'machine' from config.json fields mapping.
        """
        machine_key = self.job_fields.get('machine', 'machine')
        machine_to_intervals = {}
        for job, props in jobs.items():
            machine = props.get(machine_key)
            if machine is not None:
                if machine not in machine_to_intervals:
                    machine_to_intervals[machine] = []
                machine_to_intervals[machine].append(job_vars[job]['interval'])
            else:
                logging.warning(f"Job {job} has no machine assigned; skipping no-overlap constraint.")
        for intervals in machine_to_intervals.values():
            if len(intervals) > 1:
                model.AddNoOverlap(intervals)

    def precedence_constraint(self, model: cp_model.CpModel, job_vars: dict, jobs: dict):
        """
        Enforce sequencing: if a job (or product block) has a 'predecessor', it must start after the predecessor ends.
        Uses the dynamic key for 'predecessor' from config.json fields mapping.
        """
        pred_key = self.job_fields.get('predecessor', 'predecessor')
        for job, props in jobs.items():
            pred = props.get(pred_key)
            if pred and pred in job_vars:
                model.Add(job_vars[job]['start'] >= job_vars[pred]['end'])
            else:
                logging.warning(f"Job {job} has no predecessor assigned or predecessor not in job_vars; skipping precedence constraint.")

    def machine_availability_constraint(self, model: cp_model.CpModel, job_vars: dict, jobs: dict):
        """
        Ensure that jobs are only scheduled on their allowed machines.
        Uses the dynamic key for 'allowed_machines' from config.json fields mapping.
        """
        allowed_machines_key = self.job_fields.get('allowed_machines', 'allowed_machines')
        machine_key = self.job_fields.get('machine', 'machine')
        for job, props in jobs.items():
            allowed_machines = props.get(allowed_machines_key)
            if allowed_machines is not None:
                machine_var = model.NewIntVarFromDomain(
                    cp_model.Domain.FromValues(allowed_machines),
                    f"{job}_machine"
                )
                model.Add(job_vars[job][machine_key] == machine_var)
            else:
                logging.warning(f"Job {job} has no allowed machines specified; skipping machine availability constraint.")

    def machine_downtime_constraint(self, model: cp_model.CpModel, job_vars: dict, jobs: dict):
        """
        Prevent jobs from being scheduled during machine downtime periods.
        Uses the dynamic key for 'downtime' from config.json fields mapping.
        """
        downtime_key = self.job_fields.get('downtime', 'downtime')
        for job, props in jobs.items():
            downtime_periods = props.get(downtime_key, [])
            if not downtime_periods:
                logging.warning(f"Job {job} has no downtime periods specified; skipping machine downtime constraint.")
            for (down_start, down_end) in downtime_periods:
                model.AddBoolOr([
                    job_vars[job]['end'] <= down_start,
                    job_vars[job]['start'] >= down_end
                ])

    def lock_sequence_constraint(self, model: cp_model.CpModel, job_vars: dict, jobs: dict):
        """
        Lock the start time and/or machine assignment for jobs/blocks that are marked as 'locked' (frozen zone).
        Uses the dynamic keys from config.json fields mapping.
        """
        locked_key = self.job_fields.get('locked', 'locked')
        locked_start_key = self.job_fields.get('locked_start', 'locked_start')
        locked_machine_key = self.job_fields.get('locked_machine', 'locked_machine')
        machine_key = self.job_fields.get('machine', 'machine')
        for job, props in jobs.items():
            if props.get(locked_key):
                if locked_start_key in props:
                    model.Add(job_vars[job]['start'] == props[locked_start_key])
                else:
                    logging.warning(f"Job {job} is locked but missing locked_start key; skipping start time lock constraint.")

                if locked_machine_key in props and machine_key in job_vars[job]:
                    model.Add(job_vars[job][machine_key] == props[locked_machine_key])
                else:
                    logging.warning(f"Job {job} is locked but missing locked_machine or machine key; skipping machine lock constraint.")


    # --------------- OBJECTIVES ---------------

    # Built-in objectives (User can add more)
    # once function is added here with , user can register it via add_objective

    def minimize_makespan(self, model: cp_model.CpModel, job_vars: dict, jobs: dict):
        """
        Objective: Minimize the makespan (maximum job end time).
        Uses the dynamic key for 'end' from config.json fields mapping.
        """
        end_key = self.job_fields.get('end', 'end')
        end_vars = [job_vars[job][end_key] for job in jobs]
        if not end_vars:
            logging.warning("No end variables found; makespan objective cannot be applied.")
        makespan = model.NewIntVar(0, int(1e9), 'makespan')
        model.AddMaxEquality(makespan, end_vars)
        return makespan

    
    def minimize_total_completion_time(self, model: cp_model.CpModel, job_vars: dict, jobs: dict):
        """
        Objective: Minimize the sum of all job end times.
        Uses the dynamic key for 'end' from config.json fields mapping.
        """
        end_key = self.job_fields.get('end', 'end')
        end_vars = [job_vars[job][end_key] for job in jobs]
        if not end_vars:
            logging.warning("No end variables found; total completion time objective cannot be applied.")
        total_completion = model.NewIntVar(0, int(1e9), 'total_completion')
        model.Add(total_completion == sum(end_vars))
        return total_completion

    def minimize_total_tardiness(self, model: cp_model.CpModel, job_vars: dict, jobs: dict):
        """
        Objective: Minimize total tardiness (lateness beyond due date).
        Uses the dynamic keys for 'due_date' and 'end' from config.json fields mapping.
        """
        due_date_key = self.job_fields.get('due_date', 'due_date')
        end_key = self.job_fields.get('end', 'end')
        tardiness_vars = []
        for job, props in jobs.items():
            due = props.get(due_date_key, 0)
            end = job_vars[job][end_key]
            if due is None:
                logging.warning(f"Job {job} has no due_date specified; assuming 0 for tardiness calculation.")
                due = 0
            if end is None:
                logging.warning(f"Job {job} has no end variable; skipping tardiness calculation for this job.")
                continue
            tardiness = model.NewIntVar(0, int(1e9), f'tardiness_{job}')
            model.Add(tardiness >= end - due)
            model.Add(tardiness >= 0)
            tardiness_vars.append(tardiness)
        total_tardiness = model.NewIntVar(0, int(1e9), 'total_tardiness')
        model.Add(total_tardiness == sum(tardiness_vars))
        return total_tardiness
    
    def minimize_total_deviation_from_planned(self, model: cp_model.CpModel, job_vars: dict, jobs: dict):
        """
        Objective: Minimize the total deviation from planned quantity (P vs A) for all jobs/blocks.
        Uses the dynamic keys for 'qty_ordered', 'qty_initialized', and 'duration' from config.json fields mapping.
        """
        qty_ordered_key = self.job_fields.get('qty_ordered', 'qty_ordered')
        qty_initialized_key = self.job_fields.get('qty_initialized', 'qty_initialized')
        duration_key = self.job_fields.get('duration', 'duration')
        deviation_vars = []
        for job, props in jobs.items():
            planned = props.get(qty_ordered_key, 0)
            if planned is None:
                logging.warning(f"Job {job} has no qty_ordered specified; assuming 0 for deviation calculation.")
                planned = 0
            # If qty_initialized is a variable in your model, use it; otherwise, use duration or another proxy
            actual = job_vars[job].get(qty_initialized_key, None)
            if actual is None:
                # Fallback: use duration as proxy for produced quantity
                actual = job_vars[job][duration_key] if duration_key in job_vars[job] else None
            if actual is not None:
                diff = model.NewIntVar(0, int(1e9), f'deviation_{job}')
                model.Add(diff == abs(planned - actual))
                deviation_vars.append(diff)
        total_deviation = model.NewIntVar(0, int(1e9), 'total_deviation')
        if deviation_vars:
            model.Add(total_deviation == sum(deviation_vars))
        else:
            model.Add(total_deviation == 0)
        return total_deviation