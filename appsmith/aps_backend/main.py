from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import date, datetime
from psycopg2.extras import execute_values
'''
from repository.db_repository import get_connection, save_schedule, add_order, fetch_orders, fetch_operations, fetch_machines, log_schedule_run, save_schedule_archive, fetch_inventory_for_item
from service.scheduler import generate_schedule, pick_machine
from routes import RouteService, RouteRepository
from models import InventoryItem, OrderRead, OrderCreate, ScheduledOperation
'''

from api import (
    machine_api,
    operation_api,
    order_api,
    inventory_api,
    product_api,
    routes_api,
)

import os
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

app.include_router(machine_api.router)
app.include_router(operation_api.router)
app.include_router(order_api.router)
app.include_router(inventory_api.router)
app.include_router(product_api.router)
app.include_router(routes_api.router)


'''
# Get Endpoints

@app.get("/schedule/gantt")
def get_schedule_gantt():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT order_id, operation, start_ts, end_ts
        FROM schedule_results
        ORDER BY start_ts
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "task": r[1],          # operation
            "start": r[2].isoformat(),
            "end": r[3].isoformat(),
            "group": f"Order {r[0]}"
        })
    return result


# Post Endpoints

@app.post("/add/sequences")
def add_sequences(sequences: List[dict] = Body(...)):
    """
    Add or update product operation sequences.
    
    :param sequences: Description
    :type sequences: List[dict]
    :example:
    [
        {"product_id": 1, "operation_id": 2, "sequence": 1},
        {"product_id": 1, "operation_id": 3, "sequence": 2},
        ...
    ]
    """
    if not sequences:
        raise HTTPException(status_code=400, detail="No sequences provided")

    conn = get_connection()
    cur = conn.cursor()

    product_ids = set(seq['product_id'] for seq in sequences if 'product_id' in seq)
    added = 0
    updated = 0

    # Prepare values for insert/update
    values = []
    operation_ids_to_keep = {seq['operation_id'] for seq in sequences}

    for seq in sequences:
        try:
            product_id = int(seq['product_id'])
            operation_id = int(seq['operation_id'])
            sequence = int(seq['sequence'])
            values.append((product_id, operation_id, sequence))
        except (KeyError, ValueError):
            continue

    if values:
        # Insert or update
        execute_values(
            cur,
            """
            INSERT INTO product_operations (product_id, operation_id, sequence)
            VALUES %s
            ON CONFLICT (product_id, operation_id)
            DO UPDATE SET sequence = EXCLUDED.sequence;
            """,
            values
        )

    # Delete any operations not in the new list for the affected products
    if operation_ids_to_keep:
        cur.execute(
            """
            DELETE FROM product_operations
            WHERE product_id = ANY(%s)
              AND operation_id NOT IN %s;
            """,
            (list(product_ids), tuple(operation_ids_to_keep))
        )

    conn.commit()
    cur.close()
    conn.close()

    return {"status": "ok", "added": added, "updated": updated}

@app.post("/run/schedule", response_model=List[ScheduledOperation])
def run_schedule(): #TODO: fix so it works with graph database
    """
    Generate and save a new production schedule based on current orders and inventory.
    This endpoint fetches all raw orders, checks if they can be scheduled based on inventory,
    generates a schedule, saves it to the database, and returns the scheduled operations.

    :return: List of scheduled operations with order ID, operation name, machine assigned, start and end times.
    :rtype: List[ScheduledOperation]
    """
    route_service = RouteService(RouteRepository(get_connection()))
    raw_orders = route_service.repo.get_all_orders() # Fetch all orders from graph database
    machines_master = fetch_machines() # Fetch all machines from relational database

    logging.info("Raw orders: %s", raw_orders)

    orders = []

    for ro in raw_orders:
        ops = []

        # Fetch operations for the order's product route (graph database)
        ops_for_order = route_service.repo.get_order_operations(ro["order_id"])

        logging.info("Operations for order %s: %s", ro["order_id"], ops_for_order)

        if not can_schedule(ops_for_order):
            logging.warning(f"Order {ro['order_id']} cannot be scheduled due to low inventory")
            continue

        for op in ops_for_order:
            machine_name = pick_machine(op["machine_type"], machines_master)
            
            ops.append({
                "name": op["name"],
                "duration": op["duration"],
                "machine": machine_name
            })

        orders.append({
            "order_id": ro["order_id"],
            "operations": ops
        })

    machines = list({m["name"] for m in machines_master})

    schedule = generate_schedule(orders, machines=machines)

    run_id = save_schedule(schedule, base_date=date.today())
    log_schedule_run(run_id)
    save_schedule_archive(schedule, run_id)

    logging.info("Schedule run %s generated", run_id)

    return schedule


# Helper functions

def can_schedule(ops_for_order):
    conn = get_connection()
    cur = conn.cursor()

    for op in ops_for_order:
        item_needed = op.get("material_needed")
        if not item_needed:
            continue
        
        qty_needed = 1  # adjust later if needed

        cur.execute("""
            SELECT COALESCE(SUM(quantity), 0)
            FROM inventory
            WHERE item_name = %s;
        """, (item_needed,))

        row = cur.fetchone()
        stock = row[0] if row is not None else 0

        if stock < qty_needed:
            logging.warning(f"Cannot schedule {op['name']}: only {stock} of {item_needed} available")
            cur.close()
            conn.close()
            return False

    cur.close()
    conn.close()
    return True

'''