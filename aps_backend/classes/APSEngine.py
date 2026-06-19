from ortools.sat.python import cp_model
from typing import List
from ProcessNode import ProcessNode
from ResourceNode import ResourceNode

class APSEngine:
    def __init__(self, horizon_days: int = 30):
        # Translate planning horizon into minutes (1 day = 1440 minutes)
        # Adjust '1440' if your data uses hours, seconds, or shifts instead of minutes
        self.horizon = horizon_days * 1440 
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        
        # Configure solver settings (e.g., stop if it takes longer than 60 seconds)
        self.solver.parameters.max_time_in_seconds = 60.0
        # Enable multi-threading for faster CPU calculation
        self.solver.parameters.num_search_workers = 4 

    def build_and_solve(self, 
                        process_nodes: List[ProcessNode], 
                        resource_nodes: List[ResourceNode]) -> str:
        """
        Translates the RAM graph into OR-Tools equations, executes the solver,
        and directly mutates the ProcessNodes with their optimized timestamps.
        """

        start_vars = {}
        end_vars = {}
        interval_vars = {}
        
        # PHASE 1: REGISTER OR-TOOLS VARIABLES ON THE PROCESS NODES
        
        for op in process_nodes:
            # Define upper/lower boundaries for times based on your planning horizon
            start_vars[op.id] = self.model.NewIntVar(0, self.horizon, f"start_{op.id}")
            end_vars[op.id] = self.model.NewIntVar(0, self.horizon, f"end_{op.id}")

            # Create the interval variable (the actual block of time OR-Tools manipulates)
            interval_vars[op.id] = self.model.NewIntervalVar(
                start_vars[op.id], 
                op.duration, 
                end_vars[op.id], 
                f"interval_{op.id}"
            )


        # PHASE 2: APPLY GRAPH-BASED CONSTRAINTS

        for op in process_nodes:
            # Rule A: Material Availability (SupplyNode Boundary)
            earliest_start = op.get_earliest_material_date()
            if earliest_start > 0:
                self.model.Add(start_vars[op.id] >= earliest_start)

            # Rule B: Sequential Operations (DAG Precedence Edges)
            for next_op in op.next_operations:
                # Downstream operation cannot start until this current operation ends
                self.model.Add(start_vars[next_op.id] >= end_vars[op.id])

        # Rule C: Machine Capacities (Bipartite Capacity Constraints)
        for resource in resource_nodes:
            # Grab all intervals competing for this specific machine/workstation
            machine_intervals = [interval_vars[op.id] for op in resource.get_all_process_nodes()]

            for start_blackout, end_blackout in resource.unavailable_windows:
                blackout_suffix = f"blackout_{resource.id}_{start_blackout}"
                maintenance_interval = self.model.NewFixedSizeIntervalVar(
                    start_blackout,
                    end_blackout - start_blackout,
                    blackout_suffix
                )
                machine_intervals.append(maintenance_interval)
            
            if machine_intervals:
                # Force OR-Tools to ensure these jobs do not stack on top of each other
                self.model.AddNoOverlap(machine_intervals)

        # PHASE 3: DEFINE THE ENGINE's OBJECTIVE

        # Common Objective: Minimize total production duration (Makespan)
        # We find the latest end time among all process nodes and try to minimize it
        makespan = self.model.NewIntVar(0, self.horizon, "makespan")
        self.model.AddMaxEquality(makespan, list(end_vars.values()))
        self.model.Minimize(makespan)

        # PHASE 4: SOLVE AND EXTRACT RESULTS

        status = self.solver.Solve(self.model)

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            # Mutate our Python objects in memory with the calculated values!
            for op in process_nodes:
                op.optimized_start = self.solver.Value(start_vars[op.id])
                op.optimized_end = self.solver.Value(end_vars[op.id])
            return "SUCCESS"
        else:
            return f"FAILED: Solver returned status code {status}"
