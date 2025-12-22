from ortools.sat.python import cp_model

def generate_schedule(orders, machines):
    """
    orders: list of dicts, e.g.,
        [{'order_id': 1, 'operations':[{'name':'Cutting','duration':2,'machine_type':'cutting'}, ...]}, ...]
    machines: list of machine dicts, e.g., [{'name': 'Cutter1', 'type': 'cutting'}, ...]
    Returns: list of scheduled operations [{'order_id', 'operation', 'machine', 'start', 'end'}]
    """
    model = cp_model.CpModel()
    all_tasks = {}
    horizon = sum(operation['duration'] for order in orders for operation in order['operations'])

    # Build a mapping from machine type to machine names
    machine_type_to_names = {}
    for machine in machines:
        machine_type_to_names.setdefault(machine['type'], []).append(machine['name'])

    # For each operation, create assignment variables for each possible machine
    operation_intervals = {}  # (order_id, op_idx, machine_name): interval_var
    operation_starts = {}     # (order_id, op_idx): start_var
    operation_ends = {}       # (order_id, op_idx): end_var
    operation_machine_bools = {}  # (order_id, op_idx, machine_name): bool_var

    for order in orders:
        prev_end = None
        for operation_idx, operation in enumerate(order['operations']):
            operation_key = (order['order_id'], operation_idx)
            operation_starts[operation_key] = model.NewIntVar(0, horizon, f"start_o{order['order_id']}_{operation_idx}")
            operation_ends[operation_key] = model.NewIntVar(0, horizon, f"end_o{order['order_id']}_{operation_idx}")
            machine_names = machine_type_to_names.get(operation['machine_type'], [])
            if not machine_names:
                raise ValueError(f"No machines available for type {operation['machine_type']}")
            # For each possible machine, create an optional interval
            operation_machine_bools[operation_key] = {}
            operation_intervals[operation_key] = {}
            for mName in machine_names:
                bool_var = model.NewBoolVar(f"is_{mName}_o{order['order_id']}_{operation_idx}")
                interval_var = model.NewOptionalIntervalVar(
                    operation_starts[operation_key], operation['duration'], operation_ends[operation_key], bool_var, f"interval_{mName}_o{order['order_id']}_{operation_idx}"
                )
                operation_machine_bools[operation_key][mName] = bool_var
                operation_intervals[operation_key][mName] = interval_var
            # Each operation must be assigned to exactly one machine
            model.AddExactlyOne([operation_machine_bools[operation_key][mname] for mname in machine_names])
            # Enforce operation sequence per order
            if prev_end is not None:
                model.Add(operation_starts[operation_key] >= prev_end)
            prev_end = operation_ends[operation_key]

    # Machine constraints: no overlaps for intervals assigned to each machine
    for machine in machines:
        mName = machine['name']
        intervals = []
        for order in orders:
            for operation_idx, operation in enumerate(order['operations']):
                operation_key = (order['order_id'], operation_idx)
                if mName in operation_intervals[operation_key]:
                    intervals.append(operation_intervals[operation_key][mName])
        if intervals:
            model.AddNoOverlap(intervals)

    # Minimize makespan
    makespan = model.NewIntVar(0, horizon, "makespan")
    model.AddMaxEquality(makespan, [operation_ends[(order['order_id'], op_idx)] for order in orders for op_idx in range(len(order['operations']))])
    model.Minimize(makespan)

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Build output
    schedule = []
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for order in orders:
            for operation_idx, operation in enumerate(order['operations']):
                operation_key = (order['order_id'], operation_idx)
                # Find which machine was assigned
                assigned_machine = None
                for mName, bool_var in operation_machine_bools[operation_key].items():
                    if solver.Value(bool_var):
                        assigned_machine = mName
                        break
                schedule.append({
                    'order_id': order['order_id'],
                    'operation': operation['name'],
                    'machine': assigned_machine,
                    'start': solver.Value(operation_starts[operation_key]),
                    'end': solver.Value(operation_ends[operation_key])
                })
    return schedule

def pick_machine(machine_type, machines):
    """
    Pick the first available machine of given type
    """
    for machine in machines:
        if machine["type"] == machine_type:
            return machine["name"]
    raise ValueError(f"No machine found for type {machine_type}")
