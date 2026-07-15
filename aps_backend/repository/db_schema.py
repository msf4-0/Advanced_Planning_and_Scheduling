"""
DDL (Data Definition Language) operations.
Handles schema changes: CREATE TABLE, ALTER COLUMN, DROP TABLE, etc.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Tables that should never be modified
DO_NOT_MODIFY_TABLES = {"pg_*", "information_schema.*"}


class SchemaManager:
    """Manages database schema — tables, columns, constraints."""
    
    def __init__(self, connection, protected_tables: Optional[List[str]] = None):
        """
        Initialize schema manager.
        
        Args:
            connection: psycopg2 connection object
            protected_tables: List of table names that cannot be modified
        """
        self.connection = connection
        self.protected_tables = protected_tables or []
    
    def _check_protected(self, table_name: str) -> None:
        """
        Check if a table is protected from modification.
        
        Raises:
            ValueError: If table is protected
        """
        if table_name in self.protected_tables:
            raise ValueError(f"Modifying table '{table_name}' is not allowed (protected)")
    
    def create_table(self, table_name: str, columns: List[Dict[str, Any]]) -> bool:
        """
        Create a new table with the specified schema.
        
        Args:
            table_name: Name of the table
            columns: List of column definitions, each with:
                - name (str): column name
                - type (str): SQL data type (e.g., "VARCHAR(100)", "INT", "SERIAL")
                - nullable (bool): allow NULL values (default: True)
                - unique (bool): add UNIQUE constraint (default: False)
                - primary_key (bool): make primary key (default: False)
                - default (str): default value SQL (e.g., "0", "NOW()")
                - foreign_key (str): foreign key reference (e.g., "other_table(id)")
        
        Returns:
            True if successful, False otherwise
            
        Example:
            columns = [
                {"name": "id", "type": "SERIAL", "primary_key": True},
                {"name": "name", "type": "VARCHAR(100)", "nullable": False},
                {"name": "category_id", "type": "INT", 
                 "foreign_key": "categories(id)"}
            ]
            schema_mgr.create_table("products", columns)
        """
        cursor = self.connection.cursor()
        try:
            column_defs = []
            
            for col in columns:
                name = col.get("name")
                col_type = col.get("type")
                
                if not name or not col_type:
                    logger.warning("Column missing name or type, skipping: %s", col)
                    continue
                
                # Build column definition
                col_def = f'"{name}" {col_type}'
                
                # Add constraints
                if not col.get("nullable", True):
                    col_def += " NOT NULL"
                
                if col.get("unique", False):
                    col_def += " UNIQUE"
                
                if col.get("primary_key", False):
                    col_def += " PRIMARY KEY"
                
                if "default" in col:
                    col_def += f" DEFAULT {col['default']}"
                
                # Foreign key is added as separate constraint (see below)
                
                column_defs.append(col_def)
            
            # Add foreign key constraints at the end
            for col in columns:
                if col.get("foreign_key"):
                    fk = col.get("foreign_key")
                    col_name = col.get("name")
                    column_defs.append(
                        f'FOREIGN KEY ("{col_name}") REFERENCES {fk}'
                    )
            
            columns_str = ", ".join(column_defs)
            sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns_str});'
            
            logger.info("Creating table '%s'", table_name)
            cursor.execute(sql)
            self.connection.commit()
            return True
            
        except Exception as e:
            self.connection.rollback()
            logger.error("Error creating table '%s': %s", table_name, e)
            return False
        finally:
            cursor.close()
    
    def drop_table(self, table_name: str, cascade: bool = False) -> bool:
        """
        Drop (delete) a table.
        
        Args:
            table_name: Name of the table to drop
            cascade: If True, drop dependent objects (default: False)
        
        Returns:
            True if successful, False otherwise
        """
        self._check_protected(table_name)
        
        cursor = self.connection.cursor()
        try:
            cascade_str = "CASCADE" if cascade else "RESTRICT"
            sql = f'DROP TABLE IF EXISTS "{table_name}" {cascade_str};'
            
            logger.info("Dropping table '%s'", table_name)
            cursor.execute(sql)
            self.connection.commit()
            return True
            
        except Exception as e:
            self.connection.rollback()
            logger.error("Error dropping table '%s': %s", table_name, e)
            return False
        finally:
            cursor.close()
    
    def add_column(self, table_name: str, columns: List[Dict[str, Any]]) -> bool:
        """
        Add one or more columns to an existing table.
        
        Args:
            table_name: Name of the table
            columns: List of column definitions (same format as create_table)
        
        Returns:
            True if successful, False otherwise
        """
        self._check_protected(table_name)
        
        cursor = self.connection.cursor()
        try:
            for col in columns:
                name = col.get("name")
                col_type = col.get("type")
                
                if not name or not col_type:
                    logger.warning("Column missing name or type, skipping: %s", col)
                    continue
                
                col_def = f'"{name}" {col_type}'
                
                if not col.get("nullable", True):
                    col_def += " NOT NULL"
                
                if col.get("unique", False):
                    col_def += " UNIQUE"
                
                if "default" in col:
                    col_def += f" DEFAULT {col['default']}"
                
                sql = f'ALTER TABLE "{table_name}" ADD COLUMN {col_def};'
                
                logger.info("Adding column '%s' to table '%s'", name, table_name)
                cursor.execute(sql)
            
            self.connection.commit()
            return True
            
        except Exception as e:
            self.connection.rollback()
            logger.error("Error adding column(s) to '%s': %s", table_name, e)
            return False
        finally:
            cursor.close()
    
    def drop_column(self, table_name: str, column_name: str, cascade: bool = False) -> bool:
        """
        Drop (delete) a column from a table.
        
        Args:
            table_name: Name of the table
            column_name: Name of the column to drop
            cascade: If True, drop dependent objects (default: False)
        
        Returns:
            True if successful, False otherwise
        """
        self._check_protected(table_name)
        
        cursor = self.connection.cursor()
        try:
            cascade_str = "CASCADE" if cascade else "RESTRICT"
            sql = f'ALTER TABLE "{table_name}" DROP COLUMN "{column_name}" {cascade_str};'
            
            logger.info("Dropping column '%s' from table '%s'", column_name, table_name)
            cursor.execute(sql)
            self.connection.commit()
            return True
            
        except Exception as e:
            self.connection.rollback()
            logger.error(
                "Error dropping column '%s' from '%s': %s",
                column_name, table_name, e
            )
            return False
        finally:
            cursor.close()
    
    def rename_column(self, table_name: str, old_name: str, new_name: str) -> bool:
        """
        Rename a column.
        
        Args:
            table_name: Name of the table
            old_name: Current column name
            new_name: New column name
        
        Returns:
            True if successful, False otherwise
        """
        self._check_protected(table_name)
        
        cursor = self.connection.cursor()
        try:
            sql = f'ALTER TABLE "{table_name}" RENAME COLUMN "{old_name}" TO "{new_name}";'
            
            logger.info("Renaming column '%s' to '%s' in table '%s'", old_name, new_name, table_name)
            cursor.execute(sql)
            self.connection.commit()
            return True
            
        except Exception as e:
            self.connection.rollback()
            logger.error(
                "Error renaming column '%s' in '%s': %s",
                old_name, table_name, e
            )
            return False
        finally:
            cursor.close()
    
    def alter_column_type(
        self,
        table_name: str,
        column_name: str,
        new_type: str,
        using_clause: Optional[str] = None
    ) -> bool:
        """
        Change the data type of a column.
        
        Args:
            table_name: Name of the table
            column_name: Name of the column
            new_type: New SQL data type
            using_clause: Optional USING clause for type conversion
                         (e.g., "CAST(column AS INTEGER)")
        
        Returns:
            True if successful, False otherwise
        
        Example:
            schema_mgr.alter_column_type(
                "products",
                "price",
                "DECIMAL(10,2)",
                using_clause="price::numeric(10,2)"
            )
        """
        self._check_protected(table_name)
        
        cursor = self.connection.cursor()
        try:
            sql = f'ALTER TABLE "{table_name}" ALTER COLUMN "{column_name}" TYPE {new_type}'
            
            if using_clause:
                sql += f" USING {using_clause}"
            
            sql += ";"
            
            logger.info("Altering column '%s' type to %s in table '%s'",
                       column_name, new_type, table_name)
            cursor.execute(sql)
            self.connection.commit()
            return True
            
        except Exception as e:
            self.connection.rollback()
            logger.error(
                "Error altering column '%s' in '%s': %s",
                column_name, table_name, e
            )
            return False
        finally:
            cursor.close()
    
    def set_column_default(self, table_name: str, column_name: str, default_value: str) -> bool:
        """
        Set a default value for a column.
        
        Args:
            table_name: Name of the table
            column_name: Name of the column
            default_value: Default value (as SQL expression, e.g., "0", "NOW()")
        
        Returns:
            True if successful, False otherwise
        """
        self._check_protected(table_name)
        
        cursor = self.connection.cursor()
        try:
            sql = f'ALTER TABLE "{table_name}" ALTER COLUMN "{column_name}" SET DEFAULT {default_value};'
            
            logger.info("Setting default for column '%s' in '%s'", column_name, table_name)
            cursor.execute(sql)
            self.connection.commit()
            return True
            
        except Exception as e:
            self.connection.rollback()
            logger.error(
                "Error setting default for column '%s': %s",
                column_name, e
            )
            return False
        finally:
            cursor.close()
    
    def drop_column_default(self, table_name: str, column_name: str) -> bool:
        """
        Remove the default value from a column.
        
        Args:
            table_name: Name of the table
            column_name: Name of the column
        
        Returns:
            True if successful, False otherwise
        """
        self._check_protected(table_name)
        
        cursor = self.connection.cursor()
        try:
            sql = f'ALTER TABLE "{table_name}" ALTER COLUMN "{column_name}" DROP DEFAULT;'
            
            logger.info("Dropping default for column '%s' in '%s'", column_name, table_name)
            cursor.execute(sql)
            self.connection.commit()
            return True
            
        except Exception as e:
            self.connection.rollback()
            logger.error(
                "Error dropping default for column '%s': %s",
                column_name, e
            )
            return False
        finally:
            cursor.close()
