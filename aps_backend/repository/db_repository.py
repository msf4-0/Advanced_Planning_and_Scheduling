import os
import psycopg2
import logging
from typing_extensions import Any, Optional
from psycopg2.extras import RealDictCursor
from datetime import datetime
from enum import Enum

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgresUser")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgresPass")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgresDB")

run_id = datetime.now().isoformat()

class TableName(Enum):
    INVENTORY = "inventory"
    MACHINE_TYPES = "machine_types"
    MACHINES = "machines"
    MATERIALS = "materials"
    OPERATIONS = "operations"
    ORDERS = "orders"
    PRODUCT_BLUEPRINT = "product_blueprint"
    PRODUCTS = "products"
    SCHEDULE_RUNS = "schedule_runs"
    SCHEDULE_STEPS = "schedule_steps"

class DBTable:
        
    def __init__(self):
        self.db_params = {
            "host": POSTGRES_HOST,
            "port": POSTGRES_PORT,
            "user": POSTGRES_USER,
            "password": POSTGRES_PASSWORD,
            "dbname": POSTGRES_DB
        }

    def get_connection_graph(self):
        conn = psycopg2.connect(**self.db_params)
        # Ensure PostgreSQL session uses UTC
        with conn.cursor() as cur:
            cur.execute("SET TIME ZONE 'UTC';")
            cur.execute("CREATE EXTENSION IF NOT EXISTS age;")
            cur.execute("LOAD 'age';")
            cur.execute("SET search_path = ag_catalog, \"$user\", public;")
        return conn
    
    def get_connection(self):
        conn = psycopg2.connect(**self.db_params)
        # Ensure PostgreSQL session uses UTC
        with conn.cursor() as cur:
            cur.execute("SET TIME ZONE 'UTC';")
        return conn

    # Fetch functions

    def fetch(self, table_name: str, params: Optional[dict] = None, table_list: Optional[list[str]] = None) -> list[dict[str, Any]]:
        """
        Fetch all records from a specified table with optional filtering parameters.

        Args:
            table_name (str): The name of the table to fetch records from.
            params (Optional[dict]): A dictionary of column-value pairs to filter the results.
            
            Example:
                params = {"item_id": 1, "item_name": "Widget"}

        Returns:
            list[dict]: A list of records represented as dictionaries.
        """

        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            if table_list:
                if table_name not in table_list:
                    raise ValueError("Table name not in allowed table list")

            query = f"SELECT * FROM {table_name}"
            values = []
            if params:
                filters = []
                for key, value in params.items():
                    filters.append(f"{key} = %s")
                    values.append(value)
                query += " WHERE " + " AND ".join(filters)
            query += ";"
            cur.execute(query, tuple(values))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            logging.error("Error fetching from %s: %s", table_name, e)
            return []
        finally:
            cur.close()
            conn.close()

    def add(self, table_name: str, data: dict, table_list: Optional[list[str]] = None) -> list[dict[str, Any]]:
        """
        Add a new record to a specified table.

        Args:
            table_name (str): The name of the table to add the record to.
            data (dict): A dictionary of column-value pairs representing the new record.

            Example:
                data = {"item_name": "Widget", "quantity": 100, "min_required": 10, "max_capacity": 500}

        Returns:
            list[dict]: A list containing the newly added record as a dictionary.
        """

        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            if table_list:
                if table_name not in table_list:
                    raise ValueError("Table name not in allowed table list")

            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING *;"
            cur.execute(query, tuple(data.values()))
            new_record = cur.fetchall()
            conn.commit()
            return new_record
        except Exception as e:
            logging.error("Error adding to %s: %s", table_name, e)
            return []
        finally:
            cur.close()
            conn.close()

    def delete(self, table_name: str, conditions: dict, table_list: Optional[list[str]] = None) -> int:
        """
        Delete records from a specified table based on given conditions.

        Args:
            table_name (str): The name of the table to delete records from.
            conditions (dict): A dictionary of column-value pairs to identify records to delete.

            Example:
                conditions = {"item_id": 1}

        Returns:
            int: The number of records deleted.
        """
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            if table_list:
                if table_name not in table_list:
                    raise ValueError("Table name not in allowed table list")

            query = f"DELETE FROM {table_name}"
            values = []
            if conditions:
                filters = []
                for key, value in conditions.items():
                    filters.append(f"{key} = %s")
                    values.append(value)
                query += " WHERE " + " AND ".join(filters)
            query += ";"
            cur.execute(query, tuple(values))
            deleted_count = cur.rowcount
            conn.commit()
            return deleted_count
        except Exception as e:
            logging.error("Error deleting from %s: %s", table_name, e)
            return 0
        finally:
            cur.close()
            conn.close()

    def update(self, table_name: str, data: dict, conditions: dict, table_list: Optional[list[str]] = None) -> int:
        """
        Update records in a specified table based on given conditions.
        Args:
            table_name (str): The name of the table to update records in.
            data (dict): A dictionary of column-value pairs representing the new data.
            conditions (dict): A dictionary of column-value pairs to identify records to update.

            Example:
                data = {"quantity": 50, "status": "completed"}
                conditions = {"order_id": 1}

        Returns:
            int: The number of records updated.
        """

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            if table_list:
                if table_name not in table_list:
                    raise ValueError("Table name not in allowed table list")

            set_clauses = []
            values = []
            for key, value in data.items():
                set_clauses.append(f"{key} = %s")
                values.append(value)
            query = f"UPDATE {table_name} SET " + ", ".join(set_clauses)

            if conditions:
                filters = []
                for key, value in conditions.items():
                    filters.append(f"{key} = %s")
                    values.append(value)
                query += " WHERE " + " AND ".join(filters)
            query += ";"
            cur.execute(query, tuple(values))
            updated_count = cur.rowcount
            conn.commit()
            return updated_count
        except Exception as e:
            logging.error("Error updating %s: %s", table_name, e)
            return 0
        finally:
            cur.close()
            conn.close()

    def upsert(self, table_name: str, data: dict, conflict_columns: list[str], table_list: Optional[list[str]] = None) -> list[dict[str, Any]]:
        """
        Upsert a record in a specified table based on conflict columns.
        Args:
            table_name (str): The name of the table to upsert the record in.
            data (dict): A dictionary of column-value pairs representing the record.
            conflict_columns (list[str]): A list of columns to check for conflicts.

            Example:
                data = {"item_id": 1, "item_name": "Widget", "quantity": 100}
                conflict_columns = ["item_id"]

        Returns:
            list[dict]: A list containing the upserted record as a dictionary.
        """

        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            if table_list:
                if table_name not in table_list:
                    raise ValueError("Table name not in allowed table list")

            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            update_clauses = ', '.join([f"{key} = EXCLUDED.{key}" for key in data.keys() if key not in conflict_columns])
            conflict_cols = ', '.join(conflict_columns)

            query = f"""
                INSERT INTO {table_name} ({columns})
                VALUES ({placeholders})
                ON CONFLICT ({conflict_cols}) DO UPDATE
                SET {update_clauses}
                RETURNING *;
            """
            cur.execute(query, tuple(data.values()))
            upserted_record = cur.fetchall()
            conn.commit()
            return upserted_record
        except Exception as e:
            logging.error("Error upserting into %s: %s", table_name, e)
            return []
        finally:
            cur.close()
            conn.close()

    def fetch_counts(self, table_name: str) -> int:
        """
        Fetch the count of records in a specified table.

        Args:
            table_name (str): The name of the table to count records from.
        Returns:
            int: The count of records in the table.
        """
        conn = self.get_connection()
        cur = conn.cursor()
        ALLOWED_TABLES = {"inventory", "orders", "machines", "materials", "products"}  # add all allowed table names

        try:
            if table_name not in ALLOWED_TABLES:
                raise ValueError("Invalid table name")
            
            cur.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cur.fetchone()[0]
            return count
        except Exception as e:
            logging.error("Error fetching counts from %s: %s", table_name, e)
            return 0
        finally:
            cur.close()
            conn.close()

    def create_table(self, table_name: str, columns: list[dict]) -> bool:
        """
        Create a new table in the database with the specified schema.

        Args:
            table_name (str): The name of the table to create.
            columns (list[dict]): A list of dicts, each with keys:
                - name (str): column name
                - type (str): SQL data type
                - default (optional): default value
                - nullable (optional): bool
                - primary_key (optional): bool
                - unique (optional): bool
                - foreign_key (optional): str, e.g. 'other_table(other_id)'

            Example:
                columns = [
                    {"name": "item_id", "type": "SERIAL", "primary_key": True},
                    {"name": "item_name", "type": "VARCHAR(100)", "nullable": False},
                    {"name": "quantity", "type": "INT", "default": 0, "nullable": True},
                    {"name": "category_id", "type": "INT", "foreign_key": "categories(category_id)"}
                ]

        Returns:
            bool: True if the table was created successfully, False otherwise.
        """
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            column_defs = []
            for col in columns:
                col_def = f"{col['name']} {col['type']}"
                if not col.get("nullable", True):
                    col_def += " NOT NULL"
                if col.get("unique", False):
                    col_def += " UNIQUE"
                if "default" in col:
                    col_def += f" DEFAULT {col['default']}"
                column_defs.append(col_def)
            columns_str = ", ".join(column_defs)
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str});"
            logging.info("Creating table with query: %s", query)
            cur.execute(query)
            conn.commit()
            return True
        except Exception as e:
            logging.error("Error creating table %s: %s", table_name, e)
            return False
        finally:
            cur.close()
            conn.close()

    def add_table_column(self,
                         table_name: str,
                         column: list[dict]
                        ) -> bool:
        """
        Add one or more columns to an existing table.

        Args:
            table_name (str): The name of the table to alter.
            column (list[dict]): List of column definitions (same format as create_table).

        Returns:
            bool: True if columns added successfully, False otherwise.
        """
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            for col in column:
                name = col.get("name")
                type_ = col.get("type")
                default = col.get("default")
                nullable = col.get("nullable", True)
                unique = col.get("unique", False)
                primary_key = col.get("primary_key", False)
                foreign_key = col.get("foreign_key")
                if not name or not type_:
                    logging.warning("Column name or type missing, skipping column: %s", col)
                    continue
                col_def = f"{name} {type_}"
                if not nullable:
                    col_def += " NOT NULL"
                if unique:
                    col_def += " UNIQUE"
                if default not in (None, ""):
                    col_def += f" DEFAULT {default}"
                # Add column
                query = f"ALTER TABLE {table_name} ADD COLUMN {col_def};"
                logging.info("Adding column with query: %s", query)
                cur.execute(query)
                # Add primary key (only possible if table has no PK yet, otherwise skip)
                if primary_key:
                    try:
                        pk_query = f"ALTER TABLE {table_name} ADD PRIMARY KEY ({name});"
                        cur.execute(pk_query)
                    except Exception as pk_e:
                        logging.warning("Could not add primary key for column %s: %s", name, pk_e)
                # Add foreign key
                if foreign_key:
                    try:
                        fk_query = f"ALTER TABLE {table_name} ADD FOREIGN KEY ({name}) REFERENCES {foreign_key};"
                        cur.execute(fk_query)
                    except Exception as fk_e:
                        logging.warning("Could not add foreign key for column %s: %s", name, fk_e)
            conn.commit()
            return True
        except Exception as e:
            logging.error("Error adding column(s) to table %s: %s", table_name, e)
            return False
        finally:
            cur.close()
            conn.close()

    def remove_table_column(self,
                            table_name: str,
                            column_name: str
                            ) -> bool:
        """
        Remove a column from a specified table.
        Args:
            table_name (str): The name of the table from which to remove the column.
            column_name (str): The name of the column to remove.
        Returns:
            bool: True if the column was removed successfully, False otherwise.
        """
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            query = f"ALTER TABLE {table_name} DROP COLUMN {column_name};"
            cur.execute(query)
            conn.commit()
            return True
        except Exception as e:
            logging.error("Error removing column %s from table %s: %s", column_name, table_name, e)
            return False
        finally:
            cur.close()
            conn.close()

    def edit_table_column(self, 
                          table_name: str, 
                          old_column_name: str, 
                          new_column_name: str, 
                          new_data_type: str,
                          default_value: Optional[Any] = None
                          ) -> bool:
        """
        Edit the data type of an existing column in a specified table.

        Args:
            table_name (str): The name of the table containing the column to edit.
            old_column_name (str): The current name of the column to edit.
            new_column_name (str): The new name for the column.
            new_data_type (str): The new SQL data type for the column.
            default_value (Optional[Any]): The default value for the column, if any.
            Example:
                new_data_type = "VARCHAR(200)"

        Returns:
            bool: True if the column was edited successfully, False otherwise.
        """
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            query = f"ALTER TABLE {table_name} RENAME COLUMN {old_column_name} TO {new_column_name};"
            cur.execute(query)
            query = f"ALTER TABLE {table_name} ALTER COLUMN {new_column_name} TYPE {new_data_type};"
            cur.execute(query)
            if default_value is not None:
                query = f"ALTER TABLE {table_name} ALTER COLUMN {new_column_name} SET DEFAULT %s;"
                cur.execute(query, (default_value,))

            conn.commit()
            return True
        except Exception as e:
            logging.error("Error editing column %s in table %s: %s", old_column_name, table_name, e)
            return False
        finally:
            cur.close()
            conn.close()