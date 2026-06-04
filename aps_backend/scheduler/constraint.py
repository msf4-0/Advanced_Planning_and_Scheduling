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
        self.add_constraint(self.prep_job_constraint)

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
        Enforce sequencing: if a job has predecessors, it must start after ALL predecessors end (tight packing).
        Handles both 'predecessor' (single ID) and 'predecessors' (list of IDs).
        """
        for job, props in jobs.items():
            # Aggregate all possible predecessors from both singular and plural keys
            preds = set()
            
            # Check single 'predecessor' key
            if props.get('predecessor'):
                preds.add(props['predecessor'])
                
            # Check 'predecessors' list key
            multi_preds = props.get('predecessors')
            if isinstance(multi_preds, list):
                preds.update(multi_preds)

            for pred in preds:
                if pred in job_vars:
                    model.Add(job_vars[job]['start'] >= job_vars[pred]['end'])
                else:
                    logging.warning(f"Job {job}: Predecessor '{pred}' not found in job_vars; skipping this link.")

    def no_overlap_constraint(self, model: cp_model.CpModel, job_vars: dict, jobs: dict):
        """
        Ensure no two jobs assigned to the same resource overlap in time.
        Handles BOTH fixed resources (in job properties) AND dynamic resource assignments.
        """
        # Method 1: Fixed resources (existing behavior)
        resources_to_intervals = {}
        for job, props in jobs.items():
            fixed_resources = props.get('resources')  # If explicitly set
            if fixed_resources is not None:
                if fixed_resources not in resources_to_intervals:
                    resources_to_intervals[fixed_resources] = []
                resources_to_intervals[fixed_resources].append(job_vars[job]['interval'])
        
        # Apply no-overlap for fixed resources
        for intervals in resources_to_intervals.values():
            if len(intervals) > 1:
                model.AddNoOverlap(intervals)
        
        # Method 2: Dynamic resources (decision variables)
        # For jobs that can be assigned to any allowed resource
        for job_i, props_i in jobs.items():
            if props_i.get('resources') is None:  # Not pre-assigned
                for job_j, props_j in jobs.items():
                    if job_i < job_j and props_j.get('resources') is None:  # Avoid duplicates
                        # If both jobs assigned to same machine, they cannot overlap
                        resource_i = job_vars[job_i]['resources']
                        resource_j = job_vars[job_j]['resources']
                        
                        # Create implication: if same resource, then no overlap
                        # If resource_i == resource_j, then intervals don't overlap
                        for res in set(list(props_i.get('allowed_resources', [1])) + 
                                    list(props_j.get('allowed_resources', [1]))):
                            # When both are assigned to res, enforce no-overlap
                            model.Add(job_vars[job_i]['end'] <= job_vars[job_j]['start']).OnlyEnforceIf(
                                [resource_i == res, resource_j == res]
                            )
                            model.Add(job_vars[job_j]['end'] <= job_vars[job_i]['start']).OnlyEnforceIf(
                                [resource_i == res, resource_j == res]
                            )

    def prep_job_constraint(self, model: cp_model.CpModel, job_vars: dict, jobs: dict):
        """
        Enforce that prep jobs start before main jobs.
        Job property: 'prep_for' = {'job_name': 'target_job', 'days_before': 1}
        Example: prep job must start 1 day (24 time units) before the target job starts.
        """
        for job, props in jobs.items():
            prep_config = props.get('prep_for')
            if prep_config:
                target_job = prep_config.get('job_name')
                days_before = prep_config.get('days_before', 1)
                offset = days_before * 24  # Convert days to time units
                
                if target_job in job_vars:
                    # prep job must start at least 'offset' time units before target job starts
                    model.Add(job_vars[job]['end'] <= job_vars[target_job]['start'])
                    model.Add(job_vars[target_job]['start'] >= job_vars[job]['start'] + offset)
                else:
                    logging.warning(f"Job {job}: Prep target '{target_job}' not found.")