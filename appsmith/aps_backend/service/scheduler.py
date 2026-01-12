from collections import defaultdict
from typing import Optional
from ortools.sat.python import cp_model
from service import OpStepService
from repository import GraphEditor, DBTable
import logging
import pprint

class Schedule():
    def __init__(self):
        """
        Initialize the Schedule class.
        """
        self.db = DBTable()
        self.graph_editor = GraphEditor(self.db)
        self.service = OpStepService(self.graph_editor)

        self.current_time = 0
        self.completed_schedule = []
        self.machines = {}

        # Initialize machines from the database
        for machine in self.db.fetch_machines():
            machine_typeID = machine['type_id']
            machine_name = machine['name']
            if machine_typeID not in self.machines:
                self.machines[machine_typeID] = []
            self.machines[machine_typeID].append(machine_name) # Store machine names {machine_type: [machine_names]}

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

    def create_schedule(self, max_horizon: int) -> int:
        """
        Main scheduling loop.
        
        :param self: Description
        :param max_horizon: Maximum time horizon for scheduling (make sure time scale is consistent)
        :type max_horizon: int
        """

        conn = self.db.get_connection()

        schedule_run_id = self.db.create_schedule_run(max_horizon)
        scheduled_steps = set()  # Track OpSteps already scheduled

        running_id = self.db.fetch_schedule_runs(status='running')
        if running_id:
            raise Exception(f"Schedule run {running_id[0]['id']} is still running. Cannot start a new schedule.")

        logging.info(f"Starting scheduling with max_horizon: {max_horizon}")

        while self.current_time < max_horizon:
            # Fetch ready OpSteps from AGE
            logging.info(f"Current time: {self.current_time}")
            ready_steps = self.service.get_ready_opsteps()
            logging.info(f"Ready steps fetched: {[step.sequence_num for step in ready_steps]}")
            logging.info(f"Details\n%s", pprint.pformat([step for step in ready_steps]))

            if not ready_steps:
                logging.info(f"No ready steps at time {self.current_time}, advancing time...")
                self.current_time += 1
                continue

            logging.info(f"Found {len(ready_steps)} ready steps at time {self.current_time}")
            # Flatten OpSteps into OR-Tools input
            step_data = []
            for step in ready_steps:
                if step.sequence_num not in scheduled_steps:  # Only schedule once
                    step_data.append(step)
                    
                    logging.info(f"Ready step added for scheduling: {step.sequence_num} (Order {step.order_id})")

            logging.info(f"Total ready steps to schedule: {len(step_data)}")
            logging.info(f"Steps\n%s", pprint.pformat([step for step in step_data]))


            # Build OR-Tools model for this batch
            model = cp_model.CpModel()
            step_vars = {}
            machines = {}  # machine_type -> list of intervals

            # Define variables
            horizon = max_horizon
            for step in step_data:
                step_vars[step.sequence_num] = model.NewIntVar(0, horizon, f"start_{step.sequence_num}")
                if step.operation.machine_type not in machines:
                    machines[step.operation.machine_type] = []

            # Add machine constraints
            for step in step_data:
                start_var = step_vars[step.sequence_num]
                duration = step.operation.duration

                interval = model.NewIntervalVar(start_var, duration, start_var + duration, f"interval_{step.sequence_num}")
                machines[step.operation.machine_type].append(interval)

            for machine_type, intervals in machines.items():
                demands = [1] * len(intervals)
                capacity = len(self.machines.get(machine_type, []))  # Assuming total_machines is the capacity for each machine
                model.AddCumulative(intervals, demands, capacity)

            id_to_sequence = {step.op_step_id: step.sequence_num for step in step_data}

            # Add NEXT_OPERATION constraints
            for step in step_data:
                next_edges = self.graph_editor.get_edges(
                    from_id=step.op_step_id, 
                    edge_type='NEXT_OPERATION', 
                    conn=conn
                )
                for edge in next_edges:
                    logging.info(f"Processing NEXT_OPERATION edge: {edge} for step {step.sequence_num}")
                    logging.info(f"Edge end_id: {edge['end_id']}")
                    logging.info(f"Current id_to_sequence mapping: {id_to_sequence}")
                    logging.info(edge['end_id'] in id_to_sequence)

                    if edge['end_id'] in id_to_sequence:
                        logging.info(f"Adding NEXT_OPERATION constraint from step {step.sequence_num} to step {edge}")
                        next_seq = id_to_sequence[edge['end_id']]
                        model.Add(step_vars[step.sequence_num] + step.operation.duration <= step_vars[next_seq])

            logging.info(f"Step variables: {step_vars}")
            logging.info(f"Machine constraints: {machines}")
            logging.info(f"Model built with {len(step_data)} steps. Solving...")

            # Solve the model
            solver = cp_model.CpSolver()
            status = solver.Solve(model)
            
            logging.info(f"Solver status at time {self.current_time}: {solver.StatusName(status)}")

            if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                for step in step_data:
                    sequence_num = step.sequence_num
                    start_time = solver.Value(step_vars[sequence_num])

                    logging.info(f"Scheduling step {sequence_num} at time {start_time}")
                    
                    # Mark step RUNNING
                    if sequence_num not in scheduled_steps:
                        logging.info(f"Updating step {sequence_num} status to 'running' in AGE. \nRaw node: {step}")
                        updated_node = self.graph_editor.update_node(
                            step.op_step_id, 
                            {
                            'status': 'running',
                            'start_time': start_time
                            },
                            conn=conn
                        )

                        logging.info(f"Step {sequence_num} updated node: {updated_node}")

                        # Record in completed schedule

                        order = self.db.fetch_orders(step.order_id)  # ensure order exists and fetch product_id
                        
                        self.completed_schedule.append({
                            'order_id': step.order_id,
                            'product_id': order[0]['product_id'] if order else None,
                            'sequence_num': step.sequence_num,
                            'operation_id': step.operation.operation_id,
                            'start_time': start_time,
                            'duration': step.operation.duration,
                            'machine_type': step.operation.machine_type
                        })

                        scheduled_steps.add(sequence_num)
            else:
                print("No solution found for current ready steps.")
                self.current_time += 1  # Advance time if no solution
                continue

            # Advance time
            self.current_time += 1

            # Check if all operations are done
            running_steps = self.graph_editor.get_node('OpStep', {'status': 'running'}, conn=conn)
            op_detail = self.db.fetch_operations()

            for step in running_steps:
                if self.current_time >= step['start_time'] + op_detail[0]['duration']:
                    # Mark step DONE
                    self.graph_editor.update_node(step['id'], {'status': 'done'}, conn=conn)

            self.all_done = len(self.graph_editor.get_node('OpStep', {'status': 'pending'}, conn=conn)) == 0
            if self.all_done:
                break

        # Save completed schedule to DB
        
        self.machine_assigner()
        # Prevent duplicate schedule steps from being saved
        saved_steps = set()  # (schedule_run_id, sequence_num)
        for step in self.completed_schedule:
            key = (schedule_run_id, step['sequence_num'])
            if key not in saved_steps:
                self.db.save_schedule_step(schedule_run_id, step)
                saved_steps.add(key)

        conn.commit()
        conn.close()
    
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