from ortools.sat.python import cp_model
from service import ProductBlueprintService, OpStepService
from repository import GraphEditor, DBTable

class Schedule():
    def __init__(self, orders=None, operations=None, total_machines=0):
        self.all_done = False
        self.completed_schedule = {}
        self.model = cp_model.CpModel()
        self.conn = DBTable().get_connection()
        self.graph_editor = GraphEditor(self.conn)
        self.service = OpStepService(self.graph_editor)
        self.orders = orders
        self.operations = operations
        self.total_machines = total_machines
        self.current_time = 0

        if orders and operations and total_machines > 0:
            self.generate_initial_schedule()
        else:
            raise ValueError("Insufficient parameters to initialize Schedule")

    def reset(self):
        self.all_done = False
        self.completed_schedule = {}
        self.model = cp_model.CpModel()
        self.current_time = 0

    def generate_initial_schedule(self, max_horizon: int = 480):
        """
        Main scheduling loop.
        
        :param self: Description
        :param max_horizon: Maximum time horizon for scheduling
        :type max_horizon: int
        """

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

            for machine_intervals in machines.values():
                model.AddNoOverlap(machine_intervals)

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
                    start_time = solver.Value(step_vars[step['sequence_id']])
                    # Mark step RUNNING
                    self.graph_editor.update_node(
                        step['sequence_id'], 
                        {
                        'status': 'running',
                        'start_time': start_time
                        }
                    )
                    print(f"Scheduled OpStep {step['sequence_id']} (Order {step['order_id']}) at time {start_time}")
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
                    print(f"Completed OpStep {step['id']} at time {self.current_time}")

            self.all_done = len(self.graph_editor.get_node('OpStep', {'status': 'pending'})) == 0
            print(f"All done: {self.all_done}")


