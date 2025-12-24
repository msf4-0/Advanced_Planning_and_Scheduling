import os
import psycopg2
import logging
import uuid
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgresUser")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgresPass")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgresDB")

run_id = datetime.now().isoformat()

def get_connection():
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB
    )

    cur = conn.cursor()
    cur.execute("SELECT current_database(), current_user, inet_server_addr();")
    logging.info("DB INFO: %s", cur.fetchone())
    cur.close()

    return conn

# Fetch functions

def fetch_inventory():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM inventory;")
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
            "received_at": r[6]
        }
        for r in rows
    ]


def fetch_orders():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM orders;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def fetch_operations():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT operation_id, name, duration, required_machine_type
        FROM operations
        ORDER BY operation_id
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "name": r[1],
            "duration": r[2],
            "machine_type": r[3],
        }
        for r in rows
    ]


def fetch_machines():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT machine_id, name, type
        FROM machines
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "name": r[1],
            "type": r[2],
        }
        for r in rows
    ]


def fetch_order_operations(product_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            o.name,
            o.duration,
            o.required_machine_type,
            po.sequence,
            o.material_needed
        FROM product_operations po
        JOIN operations o ON po.operation_id = o.operation_id
        JOIN products p ON po.product_id = p.product_id
        WHERE p.product_name = %s
        ORDER BY po.sequence;
    """, (product_name,))
    
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "name": r[0],
            "duration": r[1],
            "machine_type": r[2],
            "sequence": r[3],
            "material_needed": r[4]
        }
        for r in rows
    ]


def fetch_inventory_for_item(item_needed):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * 
        FROM inventory 
        WHERE item_name = %s
    """, (item_needed,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        return {
            "item_id": row[0],
            "item_name": row[1],
            "quantity": row[2],
            "min_required": row[3],
            "max_capacity": row[4],
            "last_updated": row[5],
            "received_at": row[6]
        }
    else:
        return None


# Add functions

def add_order(order):
    """
    order: pydantic Order model
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO orders (product_name, priority, due_date, quantity)
            VALUES (%s, %s, %s, %s)
            """,
            (
                order.product_name,
                order.priority,
                order.due_date,
                order.quantity or 0
            )    
        )
        conn.commit()
    except Exception as e:
        logging.error("Error adding order: %s", e)
    finally:
        cur.close()
        conn.close()

# Save / Logging functions

def save_schedule(schedule, base_date=None):
    """
    schedule: list of dicts, each dict = {order_id, operation, machine, start, end}
    base_date: datetime, optional base date to calculate actual timestamps
    """

    if base_date is None:
        base_date = datetime.today().date()

    run_id = uuid.uuid4()

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("BEGIN;")

        # Optionally, delete old live schedule if you want only latest visible
        cur.execute("DELETE FROM schedule_results;")
        
        for s in schedule:
            start_dt = datetime.combine(base_date, datetime.min.time()) + timedelta(hours=s['start'])
            end_dt = datetime.combine(base_date, datetime.min.time()) + timedelta(hours=s['end'])

            cur.execute(
                """
                INSERT INTO schedule_results
                (order_id, operation, machine, start_offset, end_offset, start_ts, end_ts, run_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    s["order_id"],   # order_id first
                    s["operation"],  # operation
                    s["machine"],    # machine
                    s["start"],      # start_offset
                    s["end"],        # end_offset
                    start_dt,        # start_ts
                    end_dt,          # end_ts
                    str(run_id)      # run_id last
                )
            )

        cur.execute("COMMIT;")

        conn.commit()
    except Exception as e:
        logging.error("Error saving schedule: %s", e)
        cur.execute("ROLLBACK;")

    finally:
        cur.close()
        conn.close()

        return run_id

def log_schedule_run(run_id, note=None):
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            """
            INSERT INTO schedule_runs (run_id, run_time, note)
            VALUES (%s, NOW(), %s)
            """,
            (str(run_id), note)
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()

def save_schedule_archive(schedule, run_id, base_date=None):
    """
    Save a copy of the schedule to the archive table
    schedule: list of dicts, each dict = {order_id, operation, machine, start, end}
    run_id: UUID of the schedule run
    base_date: optional, to calculate actual timestamps
    """

    if base_date is None:
        base_date = datetime.today().date()

    conn = get_connection()
    cur = conn.cursor()
    
    try:
        for s in schedule:
            start_dt = datetime.combine(base_date, datetime.min.time()) + timedelta(hours=s['start'])
            end_dt = datetime.combine(base_date, datetime.min.time()) + timedelta(hours=s['end'])

            cur.execute(
                """
                INSERT INTO schedule_archive
                (order_id, operation, machine, start_offset, end_offset, start_ts, end_ts, run_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    s["order_id"],
                    s["operation"],
                    s["machine"],
                    s["start"],
                    s["end"],
                    start_dt,
                    end_dt,
                    str(run_id)
                )
            )
        conn.commit()
    except Exception as e:
        logging.error("Error saving schedule to archive: %s", e)
    finally:
        cur.close()
        conn.close()
