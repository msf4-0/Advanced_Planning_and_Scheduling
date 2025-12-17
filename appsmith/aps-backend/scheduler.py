from ortools.sat.python import cp_model

def generate_schedule(orders, machines):
    """
    orders: list of dicts, e.g.,
        [{'order_id': 1, 'operations':[{'name':'Cutting','duration':2,'machine':'Cutter1'}, ...]}, ...]
    machines: list of machine names
    Returns: list of scheduled operations [{'order_id', 'operation', 'machine', 'start', 'end'}]
    """
    model = cp_model.CpModel()
    all_tasks = {}
    
    # horizon: simple upper bound (sum of all durations)
    horizon = sum(operations['duration'] for order in orders for operations in order['operations'])
    
    # Create task variables
    for order in orders:
        prev_end = None
        for idx, operation in enumerate(order['operations']):
            suffix = f"o{order['order_id']}_{operation['name']}"
            start_var = model.NewIntVar(0, horizon, f"start_{suffix}")
            end_var = model.NewIntVar(0, horizon, f"end_{suffix}")
            interval_var = model.NewIntervalVar(start_var, operation['duration'], end_var, f"interval_{suffix}")
            
            all_tasks[(order['order_id'], operation['name'])] = {
                'start': start_var,
                'end': end_var,
                'interval': interval_var
            }
            
            # Enforce operation sequence per order
            if prev_end is not None:
                model.Add(start_var >= prev_end)
            prev_end = end_var
    
    # Machine constraints: no overlaps
    for machine in machines:
        machine_intervals = []
        for order in orders:
            for operation in order['operations']:
                if operation['machine'] == machine:
                    machine_intervals.append(all_tasks[(order['order_id'], operation['name'])]['interval'])
        if machine_intervals:
            model.AddNoOverlap(machine_intervals)
    
    # Minimize makespan (optional)
    makespan = model.NewIntVar(0, horizon, "makespan")
    model.AddMaxEquality(
        makespan,
        [all_tasks[(order['order_id'], operation['name'])]['end'] for order in orders for operation in order['operations']]
    )
    model.Minimize(makespan)
    
    # Solve
    solver = cp_model.CpSolver()
    solver.Solve(model)
    
    # Build output
    schedule = []
    for order in orders:
        for operation in order['operations']:
            task = all_tasks[(order['order_id'], operation['name'])]
            schedule.append({
                'order_id': order['order_id'],
                'operation': operation['name'],
                'machine': operation['machine'],
                'start': solver.Value(task['start']),
                'end': solver.Value(task['end'])
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
