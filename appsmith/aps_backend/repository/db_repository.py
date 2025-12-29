import os
import psycopg2
import logging
import uuid
from typing import Optional
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta, date

from models import OrderCreate

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgresUser")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgresPass")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgresDB")

run_id = datetime.now().isoformat()

class DBTable:
    def __init__(self):
        self.db_params = {
            "host": POSTGRES_HOST,
            "port": POSTGRES_PORT,
            "user": POSTGRES_USER,
            "password": POSTGRES_PASSWORD,
            "dbname": POSTGRES_DB
        }

    def get_connection(self):
        return psycopg2.connect(**self.db_params)

    # Fetch functions

    def fetch_inventory(self):
        """
        Fetch all inventory items from the database.
        Returns: list of inventory items with 'item_id', 'item_name', 'quantity', 'min_required', 'max_capacity', 'last_updated', 'received_at', 'material_id'
        """

        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
                    SELECT * 
                    FROM inventory
                    ORDER BY item_name, received_at;
                    """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return rows

    def fetch_orders(self, order_id: Optional[int] = None):
        """
        Fetch all orders from the database or a specific order by ID.
        Returns: list of orders with 'order_id', 'product_name', 'priority', 'due_date', 'quantity', 'status'
        """

        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if order_id is not None:
            cur.execute("SELECT * FROM orders WHERE order_id = %s;", (order_id,))
        else:
            cur.execute("SELECT * FROM orders;")
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    def fetch_operations(self, operation_id: Optional[int] = None):
        """
        Fetch all operations from the database.
        Returns: list of operations with 'operation_id', 'name', 'duration'
        """

        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        if operation_id is not None:
            cur.execute("""
                SELECT * FROM operations
                WHERE operation_id = %s
                ORDER BY operation_id
            """, (operation_id,))
            row = cur.fetchone()
            rows = [row] if row else []
        else:
            cur.execute("""
                SELECT * FROM operations
                ORDER BY operation_id
            """)
            rows = cur.fetchall()

        cur.close()
        conn.close()

        return rows

    def fetch_machines(self, machine_id: Optional[int] = None, machine_name: Optional[str] = None):
        """
        Fetch all machines from the database.
        Returns: list of machines with 'machine_id', 'name', 'capacity'
        """

        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        if machine_id is not None:
            cur.execute("""
                SELECT * FROM machines
                WHERE machine_id = %s
                ORDER BY machine_id
            """, (machine_id,))
        elif machine_name is not None:
            cur.execute("""
                SELECT * FROM machines
                WHERE name = %s
                ORDER BY machine_id
            """, (machine_name,))
        else:
            cur.execute("""
                SELECT * FROM machines
                ORDER BY machine_id
            """)
            
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return rows

    def fetch_inventory_for_item(
            self,
            item_id: Optional[int] = None, 
            item_name: Optional[str] = None,
            aggregate: bool = False
        ):
        """
        Fetch inventory details for a specific item by ID or name.
        
        :param item_id: Description
        :type item_id: Optional[int]
        :param item_name: Description
        :type item_name: Optional[str]
        :param aggregate: Description
        :type aggregate: bool
        """

        if item_id is None and item_name is None:
            raise ValueError("Either item_id or item_name must be provided")
        
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if item_id is not None:
            cur.execute("SELECT * FROM inventory WHERE item_id = %s", (item_id,))
        else:
            cur.execute("SELECT * FROM inventory WHERE item_name = %s", (item_name,))

        rows = cur.fetchone()
        cur.close()
        conn.close()

        if aggregate:
            total_qty = sum(rows['quantity'] for rows in rows) if rows else 0
            min_required = max(rows['min_required'] for rows in rows) if rows else 0
            max_capacity = sum(rows['max_capacity'] for rows in rows) if rows else 0
            last_updated = max(rows['last_updated'] for rows in rows) if rows else None
            received_at = min(rows['received_at'] for rows in rows) if rows else None

            return {
                'item_id': rows[0]['item_id'] if rows else item_id,
                'item_name': rows[0]['item_name'] if rows else item_name,
                'total_quantity': total_qty,
                'min_required': min_required,
                'max_capacity': max_capacity,
                'last_updated': last_updated,
                'received_at': received_at,
                'material_id': rows[0]['material_id'] if rows else None
            }

        return rows

    def fetch_product(self, product_id: Optional[int] = None):
        """
        Fetch product details by ID or name if provided else fetch all products.
        
        :param product_id: Description
        :type product_id: Optional[int]
        """

        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
            
        if product_id is None:
            cur.execute("SELECT * FROM products;")
            rows = cur.fetchall()
        elif product_id is not None:
            cur.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
            rows = cur.fetchone()

        cur.close()
        conn.close()

        return rows

    def fetch_material(self, material_id: Optional[int] = None, material_name: Optional[str] = None):
        """
        Fetch material details by ID or name if provided else fetch all materials.
        
        :param material_id: Description
        :type material_id: Optional[int]
        :param material_name: Description
        :type material_name: Optional[str]
        """

        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
            
        if material_id is not None:
            cur.execute("SELECT * FROM materials WHERE material_id = %s", (material_id,))
            rows = cur.fetchone()
        elif material_name is not None:
            cur.execute("SELECT * FROM materials WHERE material_name = %s", (material_name,))
            rows = cur.fetchone()
        else:
            cur.execute("SELECT * FROM materials;")
            rows = cur.fetchall()

        cur.close()
        conn.close()

        return rows

    # Add functions

    def add_order(self, order: OrderCreate):
        """
        order: object with attributes product_name, priority, due_date, quantity
        """
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO orders (product_name, priority, due_date, quantity)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    order.product_id,
                    order.priority,
                    order.due_date,
                    order.quantity
                )    
            )
            conn.commit()
            order_id = cur.fetchone()['order_id']
            return order_id
        except Exception as e:
            logging.error("Error adding order: %s", e)
        finally:
            cur.close()
            conn.close()

    def add_inventory_item(
            self, 
            item_name: str, 
            quantity: int, 
            min_required: int, 
            max_capacity: int
        ):

        """
        Add a new inventory item to the database.

        Args:
            item_name (str): The name of the inventory item.
            quantity (int): The initial quantity of the item.
            min_required (int): The minimum required quantity for the item.
            max_capacity (int): The maximum capacity for the item.

        Returns:
            int: The ID of the newly added inventory item.
        """

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO inventory (item_name, quantity, min_required, max_capacity, last_updated, received_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
                RETURNING item_id;
                """,
                (item_name, quantity, min_required, max_capacity)
            )

            item_id = cur.fetchone()['item_id']
            conn.commit()
            return item_id
        
        except Exception as e:
            logging.error("Error adding inventory item: %s", e)
        finally:
            cur.close()
            conn.close()

    def add_product(self, product_name: str):
        """
        Add a new products to the database.

        Args:
            product_name (str): The name of the product.

        Returns:
            int: The ID of the newly added product.
        """

        conn = self.get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                INSERT INTO products (product_name)
                VALUES (%s)
                ON CONFLICT (product_name) DO NOTHING
                RETURNING product_id;
                """,
                (product_name,)
            )

            product_id = cur.fetchone()['product_id']
            conn.commit()
            return product_id
        
        except Exception as e:
            logging.error("Error adding product: %s", e)
        finally:
            cur.close()
            conn.close()

    def add_operation(self, name: str, required_machine_type: str, duration: int, material_id: Optional[int] = None):
        """
        Add a new operation to the database.

        Args:
            name (str): The name of the operation.
            required_machine_type (str): The type of machine required for the operation.
            duration (int): The duration of the operation in minutes.
            material_needed (str): The material needed for the operation.

        Returns:
            int: The ID of the newly added operation.
        """

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO operations (name, required_machine_type, duration, material_needed)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (name) DO UPDATE
                SET required_machine_type = EXCLUDED.required_machine_type,
                    duration = EXCLUDED.duration,
                    material_needed = EXCLUDED.material_needed
                RETURNING operation_id;
                """, (name, required_machine_type, duration, material_id)
            )

            operation_id = cur.fetchone()['operation_id']
            conn.commit()
            return operation_id
        
        except Exception as e:
            logging.error("Error adding operation: %s", e)
        finally:
            cur.close()
            conn.close()

    def add_material(self, material_name: str):
        """
        Add a new material to the database.

        Args:
            material_name (str): The name of the material.

        Returns:
            int: The ID of the newly added material.
        """

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO materials (material_name)
                VALUES (%s)
                ON CONFLICT (material_name) DO NOTHING
                RETURNING material_id;
                """,
                (material_name,)
            )

            material_id = cur.fetchone()['material_id']
            conn.commit()
            return material_id
        
        except Exception as e:
            logging.error("Error adding material: %s", e)
        finally:
            cur.close()
            conn.close()

    def add_machine(self, name: str, machine_type: str, capacity: Optional[int] = None):
        """
        Add a new machine to the database.

        Args:
            name (str): The name of the machine.
            machine_type (str): The type/category of the machine.
            capacity (Optional[int]): The capacity of the machine.

        Returns:
            int: The ID of the newly created machine.
        """

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO machines (name, machine_type, capacity)
                VALUES (%s, %s, %s)
                RETURNING machine_id;
                """,
                (name, machine_type, capacity)
            )

            machine_id = cur.fetchone()['machine_id']
            conn.commit()
            return machine_id
        
        except Exception as e:
            logging.error("Error adding machine: %s", e)
        finally:
            cur.close()
            conn.close()

    # Update functions

    def update_inventory_item(self, item_id: int, quantity: int):
        """
        Update the quantity of an inventory item.

        Args:
            item_id (int): The ID of the inventory item.
            quantity (int): The new quantity to set.
        """

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                UPDATE inventory
                SET quantity = %s, last_updated = NOW()
                WHERE item_id = %s
                """,
                (quantity, item_id)
            )
            row = cur.fetchone()
            conn.commit()
            return row['item_name'] if row else None
        
        except Exception as e:
            logging.error("Error updating inventory item: %s", e)
        finally:
            cur.close()
            conn.close()

    # Save / Logging functions

    def save_schedule(self, schedule: list[dict], base_date: Optional[date] = None, overwrite: bool = True):
        """
        Save a production schedule to the database.

        Args:
            schedule (list[dict]): Each dict = {order_id, operation, machine, start, end} in hours.
            base_date (datetime.date, optional): Base date to calculate timestamps. Defaults to today.
            overwrite (bool): If True, clears the current live schedule before saving.

        Returns:
            uuid.UUID: Unique run ID for this schedule.
        """

        if base_date is None:
            base_date = datetime.today().date()

        run_id = uuid.uuid4()

        conn = self.get_connection()
        cur = conn.cursor()

        try:
            if overwrite:
                cur.execute("DELETE FROM schedule_results;") # Clear existing schedule
            
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

            conn.commit()
            logging.info("Schedule saved with run_id: %s", run_id)
            return run_id
        
        except Exception as e:
            conn.rollback()
            logging.error("Error saving schedule: %s", e)
            raise

        finally:
            cur.close()
            conn.close()

    def log_schedule_run(self, run_id: uuid.UUID, note=None):
        """
        Log a schedule run in the schedule_runs table.

        :args:
            run_id: UUID of the schedule run
            note: optional note about the run
        """

        conn = self.get_connection()
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
            logging.info("Logged schedule run: %s", run_id)
        
        except Exception as e:
            conn.rollback()
            logging.error("Error logging schedule run: %s", e)
            raise

        finally:
            cur.close()
            conn.close()

    def save_schedule_archive(self, schedule: list[dict], run_id: uuid.UUID, base_date=None):
        """
        Save a copy of the schedule to the archive table
        
        Args:
            schedule (list[dict]): Each dict = {order_id, operation, machine, start, end} in hours.
            run_id (uuid.UUID): Unique run ID for this schedule.
            overwrite (bool): If True, clears the current live schedule before saving.

        Returns:
            uuid.UUID: Unique run ID for this schedule.
        """

        if base_date is None:
            base_date = datetime.today().date()

        conn = self.get_connection()
        cur = conn.cursor()
        
        try:
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

            conn.commit()
            logging.info("Schedule (archive) saved with run_id: %s", run_id)
            return run_id
        
        except Exception as e:
            conn.rollback()
            logging.error("Error saving schedule (archive): %s", e)
            raise

        finally:
            cur.close()
            conn.close()
