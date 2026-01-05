from collections import defaultdict
from ortools.sat.python import cp_model
from service import ProductBlueprintService, OpStepService
from repository import GraphEditor, DBTable

class Schedule():
    def __init__(self):
        """
        Initialize the Schedule class.
        """
        self.db = DBTable()
        self.graph_editor = GraphEditor(self.db.get_connection())
        self.service = OpStepService(self.graph_editor)

        self.current_time = 0
        self.completed_schedule = []
        self.machines = {}

        # Initialize machines from the database
        for machine in self.db.fetch_machines():
            machine_type = machine['type']
            machine_name = machine['name']
            if machine_type not in self.machines:
                self.machines[machine_type] = []
            self.machines[machine_type].append(machine_name) # Store machine names {machine_type: [machine_names]}

    def reset(self):
        """
        Reset the scheduling state.
        """
        self.completed_schedule = []
        self.machines = {}
        self.current_time = 0

    def get_final_schedule(self):
        return self.completed_schedule
    
    def get_machines(self) -> dict:
        return self.machines
    
    def get_gantt_friendly_schedule(self) -> list:
        """
        Convert the completed schedule into a Gantt chart friendly format.

        :return: List of dictionaries formatted for Gantt chart visualization
        :rtype: List[Dict]
        """
        self.machine_assigner()
        gantt_data = []
        for entry in self.completed_schedule:
            gantt_data.append({
                'label': f"Order {entry['order_id']}",
                'start_ts': entry['start_time'],
                'end_ts': entry['start_time'] + entry['duration'],
                'machine': entry.get('assigned_machine', 'Unassigned'),
                'order_id': entry['order_id']
            })
        return gantt_data

    def create_schedule(self, max_horizon: int = 480):
        """
        Main scheduling loop.
        
        :param self: Description
        :param max_horizon: Maximum time horizon for scheduling (make sure time scale is consistent)
        :type max_horizon: int
        """

        schedule_run_id = self.db.create_schedule_run(max_horizon)
        scheduled_steps = set()  # Track sequence_ids already scheduled

        while self.current_time < max_horizon:
            # Fetch ready OpSteps from AGE
            ready_steps = self.service.get_ready_opsteps()

            if not ready_steps:
                print(f"No ready steps at time {self.current_time}, advancing time...")
                self.current_time += 1
                continue

            # Flatten OpSteps into OR-Tools input
            step_data = []
            for step in ready_steps:
                if step.sequence not in scheduled_steps:  # Only schedule once
                    step_data.append({
                        "order_id": step.order_id,
                        "sequence_id": step.sequence,
                        "duration": step.operation.duration,
                        "machine_type": step.operation.machine_type,
                        "material_id": step.operation.material_id,
                        })
                
            # Build OR-Tools model for this batch
            model = cp_model.CpModel()
            step_vars = {}
            machines = {}  # machine_type -> list of intervals

            horizon = max_horizon
            for step in step_data:
                step_vars[step['sequence_id']] = model.NewIntVar(0, horizon, f"start_{step['sequence_id']}")
                if step['machine_type'] not in machines:
                    machines[step['machine_type']] = []

            # Add machine constraints
            for step in step_data:
                start_var = step_vars[step['sequence_id']]
                duration = step['duration']

                interval = model.NewIntervalVar(start_var, duration, start_var + duration, f"interval_{step['sequence_id']}")
                machines[step['machine_type']].append(interval)

            for machine_type, intervals in machines.items():
                demands = [1] * len(intervals)
                capacity = len(self.machines.get(machine_type, []))  # Assuming total_machines is the capacity for each machine
                model.AddCumulative(intervals, demands, capacity)

            # Add NEXT_OPERATION constraints
            for step in step_data:
                next_edges = self.graph_editor.get_edges(
                    from_id=step['sequence_id'], edge_type='NEXT_OPERATION'
                )
                for edge in next_edges:
                    if edge['to_id'] in step_vars:
                        model.Add(step_vars[step['sequence_id']] + step['duration'] <= step_vars[edge['to_id']])

            # Solve the model
            solver = cp_model.CpSolver()
            status = solver.Solve(model)

            if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                for step in step_data:
                    sequence_id = step['sequence_id']
                    start_time = solver.Value(step_vars[step['sequence_id']])
                    
                    # Mark step RUNNING
                    if sequence_id not in scheduled_steps:
                        self.graph_editor.update_node(
                            sequence_id, 
                            {
                            'status': 'running',
                            'start_time': start_time
                            }
                        )
                    
                        self.completed_schedule.append({
                            'order_id': step['order_id'],
                            'sequence_id': step['sequence_id'],
                            'start_time': start_time,
                            'duration': step['duration'],
                            'machine_type': step['machine_type']
                        })

                        scheduled_steps.add(sequence_id)
            else:
                print("No solution found for current ready steps.")
                self.current_time += 1  # Advance time if no solution
                continue

            # Advance time
            self.current_time += 1

            # Check if all operations are done
            running_steps = self.graph_editor.get_node('OpStep', {'status': 'running'})
            for step in running_steps:
                if self.current_time >= step['start_time'] + step['operation'].duration:
                    # Mark step DONE
                    self.graph_editor.update_node(step['id'], {'status': 'done'})

            self.all_done = len(self.graph_editor.get_node('OpStep', {'status': 'pending'})) == 0
            if self.all_done:
                break

        # Save completed schedule to DB
        
        self.machine_assigner()
        for step in self.completed_schedule:
            self.db.save_schedule_step(schedule_run_id, step)
    
        return schedule_run_id
        

    def machine_assigner(self):
        """
        Assign machines to scheduled steps based on availability.
        """

        machine_instance = self.machines

        # Track machine availability
        machine_available = {machine_type: [0] * len(names) for machine_type, names in self.machines.items()}

        # Group steps by machine type and sort by start time
        steps_by_type = defaultdict(list)
        for step in self.completed_schedule:
            steps_by_type[step['machine_type']].append(step)

        for machine_type, steps in steps_by_type.items():
            steps.sort(key=lambda step: step['start_time'])
            for step in steps:
                # Find the first available machine
                for index, available_time in enumerate(machine_available[machine_type]):
                    if available_time <= step['start_time']:
                        assigned_machine = machine_instance[machine_type][index]
                        step['assigned_machine'] = assigned_machine
                        # Update machine availability
                        machine_available[machine_type][index] = step['start_time'] + step['duration']
                        break