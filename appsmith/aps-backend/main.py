from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import date, datetime
from psycopg2.extras import execute_values

from db import get_connection, save_schedule, add_order, fetch_orders, fetch_operations, fetch_machines, log_schedule_run, save_schedule_archive, fetch_order_operations, fetch_inventory_for_item
from scheduler import generate_schedule, pick_machine

import os
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

class OrderCreate(BaseModel):
    product_name: str
    priority: int
    due_date: date
    quantity: int = 0

class OrderRead(OrderCreate):
    order_id: int

class ScheduledOperation(BaseModel):
    order_id: int
    operation: str
    machine: str
    start: int
    end: int

class InventoryItem(BaseModel):
    item_id: int
    item_name: str
    quantity: int
    min_required: int
    max_capacity: int
    last_updated: datetime
    received_at: datetime
    age_days: int



# Get Endpoints

@app.get("/get/inventory", response_model=List[InventoryItem])
def get_inventory():
    """
    Retrieve the current inventory list.

    Returns a list of inventory items, including their quantities, 
    minimum required, maximum capacity, and age in days.
    """

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
            """
            SELECT item_id, item_name, quantity, min_required, max_capacity, last_updated, received_at
            FROM inventory
            ORDER BY item_name, received_at;
            """
        )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "item_id": r[0],
            "item_name": r[1],
            "quantity": r[2],
            "min_required": r[3],
            "max_capacity": r[4],
            "last_updated": r[5],
            "received_at": r[6],
            "age_days": (datetime.now() - r[6]).days
        }
        for r in rows
    ]


@app.get("/get/orders", response_model=List[OrderRead])
def get_orders():
    rows = fetch_orders()

    result = []
    for r in rows:
        result.append(OrderRead(
            order_id=r['order_id'],
            product_name=r['product_name'],
            priority=r['priority'],
            due_date=r['due_date'].isoformat() if isinstance(r['due_date'], date) else r['due_date'],
            quantity=r.get('quantity', 0)
        ))
    return result


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

@app.post("/update/inventory")
def update_inventory(item_id: int = Body(...), quantity: int = Body(...)):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE inventory
        SET quantity = %s, last_updated = NOW()
        WHERE item_id = %s
        RETURNING item_name;
        """, (quantity, item_id)
    )

    row = cur.fetchone()
    item_name = row[0] if row is not None else None
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "ok", "item_id": item_id, "item_name": item_name, "new_quantity": quantity}


@app.post("/add/inventory")
def add_inventory(item_name: str = Body(...),
                  quantity: int = Body(...),
                  min_required: int = Body(...),
                  max_capacity: int = Body(...)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO inventory (item_name, quantity, min_required, max_capacity, last_updated, received_at)
        VALUES (%s, %s, %s, %s, NOW(), NOW())
        RETURNING item_id;
        """, (item_name, quantity, min_required, max_capacity)
    )
    row = cur.fetchone()
    item_id = row[0] if row is not None else None
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "ok", "item_id": item_id, "quantity": quantity}


@app.post("/add/products")
def add_products(products: List[str] = Body(...)):
    """
    Add new products to the system.
    
    :param products: List of product names to add.
    :type products: List[str]
    :example:
    [
        "Product A",
        "Product B",
        ...
    ]
    """
    if not products:
        raise HTTPException(status_code=400, detail="No products provided")

    conn = get_connection()
    cur = conn.cursor()

    added = 0

    for product_name in products:
        try:
            cur.execute(
                """
                INSERT INTO products (product_name)
                VALUES (%s)
                ON CONFLICT (product_name) DO NOTHING;
                """, (product_name,)
            )
            if cur.rowcount > 0:
                added += 1
        except Exception as e:
            logging.error(f"Error adding product {product_name}: {e}")
            continue

    conn.commit()
    cur.close()
    conn.close()

    return {"status": "ok", "added": added}


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


@app.post("/create/orders", status_code=201)
def create_order(order: OrderCreate):
    add_order(order)
    return {"message": "Order created successfully"}


@app.post("/run/schedule", response_model=List[ScheduledOperation])
def run_schedule():
    raw_orders = fetch_orders()
    # operations_master = fetch_operations()
    machines_master = fetch_machines()

    logging.info("Raw orders: %s", raw_orders)

    orders = []

    for ro in raw_orders:
        ops = []

        ops_for_order = fetch_order_operations(ro["product_name"])

        logging.info("Operations for order %s: %s", ro["order_id"], ops_for_order)

        schedulable = can_schedule(ops_for_order)
        logging.info("Can schedule? %s", schedulable)

        if not schedulable:
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
    save_schedule_archive(run_id, schedule)

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

