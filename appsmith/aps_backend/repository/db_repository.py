import os
import psycopg2
import logging
from typing_extensions import Any, Optional
from psycopg2.extras import RealDictCursor
from datetime import datetime

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
        conn = psycopg2.connect(**self.db_params)
        with conn.cursor() as cur:
            cur.execute("LOAD 'age';")
            cur.execute("""SET search_path = ag_catalog, "$user", public;""")
        
        conn.commit()
        return conn

    # Fetch functions

    def fetch_inventory(
            self,
            item_id: Optional[int] = None, 
            item_name: Optional[str] = None,
            aggregate: bool = False
        ) -> list[dict[str, Any]]:
        """
        Fetch inventory details for a specific item by ID or name.
        
        :param item_id: Description
        :type item_id: Optional[int]
        :param item_name: Description
        :type item_name: Optional[str]
        :param aggregate: Description
        :type aggregate: bool
        """
        
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if item_id is not None:
            cur.execute("""
                        SELECT * FROM inventory 
                        WHERE item_id = %s
                        ORDER BY item_name, received_at;
                        """, (item_id,)
                        )
        elif item_name is not None:
            cur.execute("""
                        SELECT * FROM inventory 
                        WHERE item_name = %s
                        ORDER BY item_name, received_at;
                        """, (item_name,)
                        )
        else:
            cur.execute("""
                        SELECT * FROM inventory
                        ORDER BY item_name, received_at;
                        """
                        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        if aggregate:
            total_qty = sum(rows['quantity'] for rows in rows) if rows else 0
            min_required = max(rows['min_required'] for rows in rows) if rows else 0
            max_capacity = sum(rows['max_capacity'] for rows in rows) if rows else 0
            last_updated = max(rows['last_updated'] for rows in rows) if rows else None
            received_at = min(rows['received_at'] for rows in rows) if rows else None

            return [{
                'item_id': rows[0]['item_id'] if rows else item_id,
                'item_name': rows[0]['item_name'] if rows else item_name,
                'total_quantity': total_qty,
                'min_required': min_required,
                'max_capacity': max_capacity,
                'last_updated': last_updated,
                'received_at': received_at,
                'material_id': rows[0]['material_id'] if rows else None
            }]

        return rows

    def fetch_orders(self, order_id: Optional[int] = None):
        """
        Fetch all orders from the database or a specific order by ID.
        Returns: list of orders with 'order_id', 'product_name', 'priority', 'due_date', 'quantity', 'status'
        """

        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        if order_id is not None:
            cur.execute("""
                        SELECT * FROM orders 
                        WHERE order_id = %s;
                        ORDER BY priority, due_date;
                        """, (order_id,))
        else:
            cur.execute("""
                        SELECT * FROM orders
                        ORDER BY priority, due_date;
                        """)
        
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
        Returns: list of machines with 'machine_id', 'name', 'type', 'capacity'
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

    def fetch_machine_types(self, type_name: Optional[str] = None, type_id: Optional[int] = None) -> list[dict[str, Any]]:
        """
        Fetch all machine types from the database.
        Returns: list of machine types with 'type_id', 'type_name'
        """

        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        if type_id is not None:
            cur.execute("""
            SELECT * FROM machine_types
            WHERE type_id = %s
            ORDER BY type_id
        """, (type_id,))
        elif type_name is not None:
            cur.execute("""
            SELECT * FROM machine_types
            WHERE type_name = %s
            ORDER BY type_id
        """, (type_name,))
        else:
            cur.execute("""
                SELECT * FROM machine_types
                ORDER BY type_id
            """)

        rows = cur.fetchall()
        cur.close()
        conn.close()

        return rows

    # Add functions

    def add_order(self, order: OrderCreate):
        """
        Add a new order to the database.
        """
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO orders (product_id, user_priority, due_date, quantity, priority)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    order.product_id,
                    order.user_priority,
                    order.due_date,
                    order.quantity,
                    order.priority
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

    def add_operation(self, name: str, type_id: int, duration: int, material_id: Optional[int] = None):
        """
        Add a new operation to the database.

        Args:
            name (str): The name of the operation.
            type_id (int): The type ID of the machine required for the operation.
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
                INSERT INTO operations (name, type_id, duration, material_needed)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (name) DO UPDATE
                SET type_id = EXCLUDED.type_id,
                    duration = EXCLUDED.duration,
                    material_needed = EXCLUDED.material_needed
                RETURNING operation_id;
                """, (name, type_id, duration, material_id)
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

    def add_machine(self, name: str, type_id: int, capacity: Optional[int] = None):
        """
        Add a new machine to the database.

        Args:
            name (str): The name of the machine.
            type_id (int): The type/category ID of the machine (foreign key to machine_types).
            capacity (Optional[int]): The capacity of the machine.

        Returns:
            int: The ID of the newly created machine.
        """

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO machines (name, type_id, capacity)
                VALUES (%s, %s, %s)
                RETURNING machine_id;
                """,
                (name, type_id, capacity)
            )

            machine_id = cur.fetchone()['machine_id']
            conn.commit()
            return machine_id
        
        except Exception as e:
            logging.error("Error adding machine: %s", e)
        finally:
            cur.close()
            conn.close()
        
    def add_machine_type(self, type_name: str) -> int:
        """
        Add a new machine type to the machine_types table, or get its id if it already exists.

        Args:
            type_name (str): The name of the machine type.

        Returns:
            int: The ID of the machine type.
        """
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO machine_types (type_name)
                VALUES (%s)
                ON CONFLICT (type_name) DO UPDATE SET type_name = EXCLUDED.type_name
                RETURNING type_id;
                """,
                (type_name,)
            )
            type_id = cur.fetchone()[0]
            conn.commit()
            return type_id
        except Exception as e:
            logging.error("Error adding machine type: %s", e)
            return -1
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

    def create_schedule_run(self, horizon: int) -> int:

        """
        Create a new schedule run entry in the database.

        Args:
            horizon (int): The time horizon for the schedule run.

        Returns:
            int: The ID of the newly created schedule run.
        """

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO schedule_runs (horizon, created_at)
                VALUES (%s, NOW())
                RETURNING schedule_run_id;
                """,
                (horizon,)
            )

            schedule_run_id = cur.fetchone()[0]
            conn.commit()
            return schedule_run_id
        
        except Exception as e:
            conn.rollback()
            logging.error("Error creating schedule run: %s", e)
            raise e
        finally:
            cur.close()
            conn.close()

    def save_schedule_step(self, schedule_run_id: int, step: dict):
        """
        Save a scheduled step to the database.

        Args:
            schedule_run_id (int): The ID of the schedule run.
            step (dict): The scheduled step details.
        """

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO schedule_steps (
                    schedule_run_id,
                    order_id,
                    product_id,
                    op_sequence,
                    operation_id,
                    start_time,
                    end_time,
                    machine_type,
                    machine_name,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    schedule_run_id,
                    step['order_id'],
                    step['product_id'],
                    step['sequence'],
                    step['operation_id'],
                    step['start_time'],
                    step['start_time'] + step['duration'],
                    step['machine_type'],
                    step.get('assigned_machine'),
                    'PLANNED'
                )
            )
            conn.commit()
        
        except Exception as e:
            logging.error("Error saving scheduled step: %s", e)
        finally:
            cur.close()
            conn.close()