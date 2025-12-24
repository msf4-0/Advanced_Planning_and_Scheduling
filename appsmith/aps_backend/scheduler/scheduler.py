from ortools.sat.python import cp_model

#TODO: change it to be encapsulated class later

def generate_schedule(orders, machines):
    """
    orders: list of dicts, e.g.,
        [{'order_id': 1, 'operations':[{'name':'Cutting','duration':2,'machine_type':'cutting'}, ...]}, ...]
    machines: list of machine dicts, e.g., [{'name': 'Cutter1', 'type': 'cutting'}, ...]
    Returns: list of scheduled operations [{'order_id', 'operation', 'machine', 'start', 'end'}]
    """
    model = cp_model.CpModel()
    horizon = sum(operation['duration'] for order in orders for operation in order['operations'])
    all_tasks = {}
    operation_duration = {}

    for order in orders:
        for operation_idx, operation in enumerate(order['operations']):
            operation_duration[(order['order_id'], operation_idx)] = operation['duration']

    
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
            operation_starts[operation_key] = model.NewIntVar(0, horizon, f"start_order{order['order_id']}_operation{operation_idx}")
            operation_ends[operation_key] = model.NewIntVar(0, horizon, f"end_order{order['order_id']}_operation{operation_idx}")
            machine_names = machine_type_to_names.get(operation['machine_type'], [])
            if not machine_names:
                raise ValueError(f"No machines available for type {operation['machine_type']}")
            
            # For each possible machine, create an optional interval
            operation_machine_bools[operation_key] = {}
            operation_intervals[operation_key] = {}
            for mName in machine_names:
                bool_var = model.NewBoolVar(f"is_{mName}_order{order['order_id']}_operation{operation_idx}")
                interval_var = model.NewOptionalIntervalVar(
                    operation_starts[operation_key], operation['duration'], operation_ends[operation_key], bool_var, f"interval_{mName}_order{order['order_id']}_operation{operation_idx}"
                )
                operation_machine_bools[operation_key][mName] = bool_var
                operation_intervals[operation_key][mName] = interval_var
            # Each operation must be assigned to exactly one machine
            model.AddExactlyOne([operation_machine_bools[operation_key][mName] for mName in machine_names])
            # Enforce operation sequence per order
            if prev_end is not None:
                model.Add(operation_starts[operation_key] >= prev_end)
            prev_end = operation_ends[operation_key]

    # Machine constraints: no overlaps for intervals assigned to each machine
    machine_to_intervals = {}
    for machine in machines:
        machine_to_intervals[machine['name']] = []
    
    for operation_key, machine_intervals in operation_intervals.items():
        for mName, intval in machine_intervals.items():
            machine_to_intervals[mName].append(intval)

    for mName, intervals in machine_to_intervals.items():
        if intervals:
            model.AddNoOverlap(intervals)
    
    machine_loads = {}

    for machine in machines:
        mName = machine['name']
        terms = []

        for operation_key, machine_bools in operation_machine_bools.items():
            if mName in machine_bools:
                duration = operation_duration[operation_key]
                terms.append(machine_bools[mName] * duration)

        if terms:
            load_var = model.NewIntVar(0, horizon, f"load_{mName}")
            model.Add(load_var == sum(terms))
            machine_loads[mName] = load_var


    # Minimize makespan
    makespan = model.NewIntVar(0, horizon, "makespan")
    model.AddMaxEquality(makespan, [operation_ends[operation_key] for operation_key in operation_ends])
    
    max_load = model.NewIntVar(0, horizon, "max_load")
    model.AddMaxEquality(max_load, list(machine_loads.values()))
    
    model.Minimize(makespan * 1000 + max_load)

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
                assigned_machine = next(
                    mName for mName, bool_var in operation_machine_bools[operation_key].items() if solver.Value(bool_var)
                )
                
                schedule.append({
                    'order_id': order['order_id'],
                    'operation': operation['name'],
                    'machine': assigned_machine,
                    'start': solver.Value(operation_starts[operation_key]),
                    'end': solver.Value(operation_ends[operation_key])
                })
    return schedule


def build_orders_from_graph(orders_from_db, route_service):
    """
    Build orders with their operations based on the product routes.
    orders_from_db: list of dicts with 'order_id' and 'product_id'
    route_service: instance of RouteService to fetch product routes
    Returns: list of orders with operations
    """
    orders = []
    for order in orders_from_db:
        product_route = route_service.get_product_route(order['product_id'])
        operations = []
        for step in product_route.steps:
            op = step.operation
            operations.append({
                'name': op.name,
                'duration': op.duration,
                'machine_type': getattr(op, 'machine_type', None)
            })
        orders.append({
            'order_id': order['order_id'],
            'operations': operations
        })
    return orders


def pick_machine(machine_type, machines):
    """
    Pick the first available machine of given type
    """
    for machine in machines:
        if machine["type"] == machine_type:
            return machine["name"]
    raise ValueError(f"No machine found for type {machine_type}")
