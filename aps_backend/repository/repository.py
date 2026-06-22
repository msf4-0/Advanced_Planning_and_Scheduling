"""
Repository pattern implementation.
High-level data access API that orchestrates all database operations.
"""

import logging
from typing import Any, Dict, List, Optional

from .db_connection import ConnectionManager
from .db_validation import ValidationPipeline, InputValidator
from .db_query_builder import QueryBuilder
from .db_executor import QueryExecutor
from .db_transactions import TransactionManager
from .db_schema import SchemaManager

logger = logging.getLogger(__name__)


class Repository:
    """
    High-level repository for data access.
    
    Provides CRUD operations and schema management with validation and safety.
    
    Example:
        config = DatabaseConfig()
        conn_mgr = ConnectionManager(config)
        repo = Repository(
            table_name="products",
            connection_manager=conn_mgr,
            allowed_tables=["products", "categories", "inventory"]
        )
        
        # Fetch all products
        products = repo.fetch_all()
        
        # Find by ID
        product = repo.fetch_by_id(1)
        
        # Add new product
        new_product = repo.add({"name": "Widget", "price": 19.99})
        
        # Update product
        repo.update(1, {"price": 24.99})
        
        # Delete product
        repo.delete(1)
        
        # Transactions
        with repo.transaction() as tx:
            repo.delete(1)
            repo.add({"name": "Gadget", "price": 29.99})
    """
    
    def __init__(
        self,
        table_name: str,
        connection_manager: Optional[ConnectionManager] = None,
        allowed_tables: Optional[List[str]] = None,
        protected_tables: Optional[List[str]] = None
    ):
        """
        Initialize repository.
        
        Args:
            table_name: Primary table name for this repository
            connection_manager: ConnectionManager instance (creates default if None)
            allowed_tables: Whitelist of table names (None = allow all)
            protected_tables: Tables that cannot be modified via SchemaManager
        """
        self.table_name = table_name
        self.connection_manager = connection_manager or ConnectionManager()
        self.allowed_tables = allowed_tables
        self.protected_tables = protected_tables or []
        
        # Get a connection for this repository
        self.connection = self.connection_manager.get_connection()
        
        # Initialize components
        self.executor = QueryExecutor(self.connection)
        self.tx = TransactionManager(self.connection)
        self.schema = SchemaManager(self.connection, protected_tables=self.protected_tables)
    
    def __del__(self):
        """Cleanup: close connection when repository is destroyed."""
        if hasattr(self, 'connection') and self.connection:
            self.connection_manager.close_connection(self.connection)
    
    # ==================== FETCH (SELECT) ====================
    
    def fetch_all(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch all records from the table.
        
        Args:
            limit: Maximum number of rows to return
            offset: Number of rows to skip
        
        Returns:
            List of record dictionaries
        """
        builder = QueryBuilder(self.table_name)
        
        if limit:
            builder.limit(limit)
        if offset:
            builder.offset(offset)
        
        sql, params = builder.build_select()
        
        try:
            return self.executor.fetch_many(sql, params)
        except Exception as e:
            logger.error("Error fetching all from '%s': %s", self.table_name, e)
            return []
    
    def fetch_by_id(self, id_value: Any) -> Optional[Dict[str, Any]]:
        """
        Fetch a single record by its primary key.
        
        Args:
            id_value: Value of the 'id' column
        
        Returns:
            Record dictionary or None if not found
        """
        builder = QueryBuilder(self.table_name)
        builder.where("id", id_value)
        
        sql, params = builder.build_select()
        
        try:
            return self.executor.fetch_one(sql, params)
        except Exception as e:
            logger.error("Error fetching by ID from '%s': %s", self.table_name, e)
            return None
    
    def fetch_where(self, **filters) -> List[Dict[str, Any]]:
        """
        Fetch records matching filter conditions.
        
        Args:
            **filters: Keyword arguments as column=value pairs
        
        Returns:
            List of matching records
        
        Example:
            repo.fetch_where(status="active", category_id=5)
        """
        try:
            # Validate table and columns
            _, sanitized = ValidationPipeline.validate_and_sanitize_fetch(
                self.table_name,
                filters,
                self.allowed_tables
            )
        except ValueError as e:
            logger.error("Validation error: %s", e)
            return []
        
        builder = QueryBuilder(self.table_name)
        
        for col, val in sanitized.items():
            builder.where(col, val)
        
        sql, params = builder.build_select()
        
        try:
            return self.executor.fetch_many(sql, params)
        except Exception as e:
            logger.error("Error fetching with filters from '%s': %s", self.table_name, e)
            return []
    
    def fetch_one_where(self, **filters) -> Optional[Dict[str, Any]]:
        """
        Fetch first record matching filter conditions.
        
        Args:
            **filters: Keyword arguments as column=value pairs
        
        Returns:
            First matching record or None
        
        Example:
            repo.fetch_one_where(email="user@example.com")
        """
        results = self.fetch_where(**filters)
        return results[0] if results else None
    
    def count(self, **filters) -> int:
        """
        Count records, optionally with filters.
        
        Args:
            **filters: Optional filter conditions
        
        Returns:
            Number of matching records
        """
        builder = QueryBuilder(self.table_name)
        
        for col, val in (filters or {}).items():
            builder.where(col, val)
        
        sql, params = builder.build_count()
        
        try:
            result = self.executor.execute_scalar(sql, params)
            return result or 0
        except Exception as e:
            logger.error("Error counting in '%s': %s", self.table_name, e)
            return 0
    
    # ==================== ADD (INSERT) ====================
    
    def add(self, data: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """
        Insert a new record.
        
        Args:
            data: Dictionary of column-value pairs
        
        Returns:
            List containing the inserted record (with RETURNING), or None on error
        
        Example:
            result = repo.add({"name": "John", "email": "john@example.com"})
        """
        try:
            _, sanitized = ValidationPipeline.validate_and_sanitize_add(
                self.table_name,
                data,
                self.allowed_tables
            )
        except ValueError as e:
            logger.error("Validation error: %s", e)
            return None
        
        builder = QueryBuilder(self.table_name)
        sql, params = builder.build_insert(sanitized)
        
        try:
            return self.executor.execute_insert_returning(sql, params)
        except Exception as e:
            logger.error("Error adding to '%s': %s", self.table_name, e)
            return None
    
    # ==================== UPDATE ====================
    
    def update(self, id_value: Any, data: Dict[str, Any]) -> int:
        """
        Update a record by ID.
        
        Args:
            id_value: Primary key value
            data: Dictionary of column-value pairs to update
        
        Returns:
            Number of rows updated
        
        Example:
            rows_updated = repo.update(1, {"name": "Jane", "status": "active"})
        """
        try:
            _, sanitized_data, _ = ValidationPipeline.validate_and_sanitize_update(
                self.table_name,
                data,
                {"id": id_value},
                self.allowed_tables
            )
        except ValueError as e:
            logger.error("Validation error: %s", e)
            return 0
        
        builder = QueryBuilder(self.table_name)
        builder.where("id", id_value)
        
        sql, params = builder.build_update(sanitized_data)
        
        try:
            return self.executor.execute_update(sql, params)
        except Exception as e:
            logger.error("Error updating in '%s': %s", self.table_name, e)
            return 0
    
    def update_where(self, data: Dict[str, Any], **filters) -> int:
        """
        Update records matching filter conditions.
        
        Args:
            data: Dictionary of column-value pairs to update
            **filters: Filter conditions
        
        Returns:
            Number of rows updated
        
        Example:
            updated = repo.update_where(
                {"status": "inactive"},
                category_id=5
            )
        """
        if not filters:
            logger.warning("update_where called with no filters - this would update ALL rows")
            return 0
        
        try:
            _, sanitized_data, sanitized_filters = ValidationPipeline.validate_and_sanitize_update(
                self.table_name,
                data,
                filters,
                self.allowed_tables
            )
        except ValueError as e:
            logger.error("Validation error: %s", e)
            return 0
        
        builder = QueryBuilder(self.table_name)
        
        for col, val in sanitized_filters.items():
            builder.where(col, val)
        
        sql, params = builder.build_update(sanitized_data)
        
        try:
            return self.executor.execute_update(sql, params)
        except Exception as e:
            logger.error("Error updating in '%s': %s", self.table_name, e)
            return 0
    
    # ==================== DELETE ====================
    
    def delete(self, id_value: Any) -> int:
        """
        Delete a record by ID.
        
        Args:
            id_value: Primary key value
        
        Returns:
            Number of rows deleted
        """
        builder = QueryBuilder(self.table_name)
        builder.where("id", id_value)
        
        sql, params = builder.build_delete()
        
        try:
            return self.executor.execute_update(sql, params)
        except Exception as e:
            logger.error("Error deleting from '%s': %s", self.table_name, e)
            return 0
    
    def delete_where(self, **filters) -> int:
        """
        Delete records matching filter conditions.
        
        Args:
            **filters: Filter conditions
        
        Returns:
            Number of rows deleted
        
        Example:
            deleted = repo.delete_where(status="archived")
        """
        try:
            InputValidator.validate_conditions(filters)
        except ValueError as e:
            logger.error("Validation error: %s", e)
            return 0
        
        builder = QueryBuilder(self.table_name)
        
        for col, val in filters.items():
            builder.where(col, val)
        
        sql, params = builder.build_delete()
        
        try:
            return self.executor.execute_update(sql, params)
        except Exception as e:
            logger.error("Error deleting from '%s': %s", self.table_name, e)
            return 0
    
    # ==================== UPSERT ====================
    
    def upsert(self, data: Dict[str, Any], conflict_columns: List[str]) -> Optional[List[Dict[str, Any]]]:
        """
        Insert a record, or update if it conflicts on specified columns.
        
        Args:
            data: Dictionary of column-value pairs
            conflict_columns: Columns that trigger the conflict detection
        
        Returns:
            List containing the upserted record, or None on error
        
        Example:
            result = repo.upsert(
                {"email": "john@example.com", "name": "John", "updated_at": "NOW()"},
                conflict_columns=["email"]
            )
        """
        try:
            InputValidator.validate_dict(data)
            InputValidator.validate_conflict_columns(conflict_columns)
        except ValueError as e:
            logger.error("Validation error: %s", e)
            return None
        
        builder = QueryBuilder(self.table_name)
        sql, params = builder.build_upsert(data, conflict_columns)
        
        try:
            return self.executor.execute_insert_returning(sql, params)
        except Exception as e:
            logger.error("Error upserting into '%s': %s", self.table_name, e)
            return None
    
    # ==================== TRANSACTIONS ====================
    
    def transaction(self) -> TransactionManager:
        """
        Get a transaction context manager.
        
        Usage:
            with repo.transaction() as tx:
                repo.add({"name": "Record 1"})
                repo.add({"name": "Record 2"})
                # Both committed if no exception; both rolled back if exception
        """
        return self.tx
    
    # ==================== SCHEMA MANAGEMENT ====================
    
    def create_table(self, columns: List[Dict[str, Any]]) -> bool:
        """
        Create the primary table for this repository.
        
        Args:
            columns: List of column definitions
        
        Returns:
            True if successful
        """
        return self.schema.create_table(self.table_name, columns)
    
    def drop_table(self, cascade: bool = False) -> bool:
        """Drop the primary table."""
        return self.schema.drop_table(self.table_name, cascade=cascade)
    
    def add_column(self, columns: List[Dict[str, Any]]) -> bool:
        """Add columns to the primary table."""
        return self.schema.add_column(self.table_name, columns)
    
    def drop_column(self, column_name: str, cascade: bool = False) -> bool:
        """Drop a column from the primary table."""
        return self.schema.drop_column(self.table_name, column_name, cascade=cascade)
    
    def rename_column(self, old_name: str, new_name: str) -> bool:
        """Rename a column in the primary table."""
        return self.schema.rename_column(self.table_name, old_name, new_name)
    
    def alter_column_type(
        self,
        column_name: str,
        new_type: str,
        using_clause: Optional[str] = None
    ) -> bool:
        """Change a column's data type."""
        return self.schema.alter_column_type(self.table_name, column_name, new_type, using_clause)
    
    # ==================== BATCH OPERATIONS ====================
    
    def batch_add(self, data_list: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Insert multiple records in a single transaction using low-level cursors."""
        if not data_list:
            return []
        
        results = []
        original_autocommit = self.connection.autocommit
        
        try:
            self.connection.autocommit = False
            
            with self.tx:
                logger.info(f"Batch add transaction started for {len(data_list)} records")
                for data in data_list:
                    InputValidator.validate_dict(data, allow_empty=False)
                    
                    # Direct validation mapping without executing individual transactions
                    _, sanitized = ValidationPipeline.validate_and_sanitize_add(
                        self.table_name, data, self.allowed_tables
                    )
                    
                    builder = QueryBuilder(self.table_name)
                    sql, params = builder.build_insert(sanitized)
                    
                    # Use a clean, isolated row cursor dictionary factory
                    from psycopg2.extras import RealDictCursor
                    with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                        cursor.execute(sql, params)
                        rows = cursor.fetchall()
                        results.append(rows)
                        
            logger.info(f"Batch add committed: {len(results)} records inserted total")
            return results
            
        except Exception as e:
            logger.error("Batch add failed, rolling back: %s", e)
            self.connection.rollback()
            return []
            
        finally:
            self.connection.autocommit = original_autocommit

    
    def batch_update(self, updates: List[Dict[str, Any]], id_column: str = "id") -> int:
        """
        Update multiple records by ID in a single transaction.
        
        Args:
            updates: List of dicts, each with id_column + update fields
            id_column: The column to use as the primary key (default: "id")
        
        Returns:
            Total number of rows updated
        
        Example:
            updates = [
                {"id": 1, "price": 15.00, "status": "updated"},
                {"id": 2, "price": 25.00, "status": "updated"},
                {"id": 3, "price": 35.00, "status": "updated"}
            ]
            total_updated = repo.batch_update(updates)
        """
        if not updates:
            return 0
        
        total_updated = 0
        original_autocommit = self.connection.autocommit
        try:
            # Use context manager for cleaner transaction handling
            self.connection.autocommit = False
            
            with self.tx:
                logger.info(f"Batch update transaction started for {len(updates)} records")
                
                for record in updates:
                    if id_column not in record:
                        logger.warning("Record missing '%s' column, skipping: %s", id_column, record)
                        continue
                    
                    id_value = record[id_column]
                    # Remove the ID from the data dict (don't update the ID itself)
                    update_data = {k: v for k, v in record.items() if k != id_column}
                    
                    if not update_data:
                        logger.debug(f"No update data for {id_column}={id_value}, skipping")
                        continue
                    
                    builder = QueryBuilder(self.table_name)
                    builder.where(id_column, id_value)
                    sql, params = builder.build_update(update_data)

                    with self.connection.cursor() as cursor:
                        cursor.execute(sql, params)
                        total_updated += cursor.rowcount
            
            logger.info(f"Batch update committed: {total_updated} rows updated total")
            return total_updated
        except Exception as e:
            logger.error("Batch update failed, rolling back: %s", e)
            self.connection.rollback()
            return 0

        finally:
            self.connection.autocommit = original_autocommit
    
    def batch_delete(self, id_values: List[Any]) -> int:
        """
        Delete multiple records by ID in a single transaction.
        
        Args:
            id_values: List of primary key values to delete
        
        Returns:
            Total number of rows deleted
        
        Example:
            ids_to_delete = [1, 2, 3, 4, 5]
            total_deleted = repo.batch_delete(ids_to_delete)
        """
        if not id_values:
            return 0
        
        total_deleted = 0
        original_autocommit = self.connection.autocommit
        
        try:
            self.connection.autocommit = False
            
            with self.tx:
                logger.info(f"Batch delete transaction started for {len(id_values)} records")
                for id_val in id_values:
                    builder = QueryBuilder(self.table_name)
                    builder.where("id", id_val)
                    sql, params = builder.build_delete()
                    
                    with self.connection.cursor() as cursor:
                        cursor.execute(sql, params)
                        total_deleted += cursor.rowcount
                        
            logger.info(f"Batch delete committed: {total_deleted} rows deleted total")
            return total_deleted
            
        except Exception as e:
            logger.error("Batch delete failed, rolling back: %s", e)
            self.connection.rollback()
            return 0
            
        finally:
            self.connection.autocommit = original_autocommit
    
    def batch_upsert(
        self,
        data_list: List[Dict[str, Any]],
        conflict_columns: List[str]
    ) -> List[List[Dict[str, Any]]]:
        """
        Upsert multiple records in a single transaction.
        
        Args:
            data_list: List of records to upsert
            conflict_columns: Columns that trigger conflict detection
        
        Returns:
            List of upserted records
        
        Example:
            records = [
                {"email": "user1@example.com", "name": "Alice"},
                {"email": "user2@example.com", "name": "Bob"}
            ]
            results = repo.batch_upsert(records, conflict_columns=["email"])
        """
        if not data_list:
            return []
        
        results = []
        original_autocommit = self.connection.autocommit
        InputValidator.validate_conflict_columns(conflict_columns)
        
        try:
            self.connection.autocommit = False
            
            with self.tx:
                logger.info(f"Batch upsert transaction started for {len(data_list)} records")
                for data in data_list:
                    InputValidator.validate_dict(data)
                    
                    builder = QueryBuilder(self.table_name)
                    sql, params = builder.build_upsert(data, conflict_columns)
                    
                    from psycopg2.extras import RealDictCursor
                    with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                        cursor.execute(sql, params)
                        rows = cursor.fetchall()
                        results.append(rows)
                        
            logger.info(f"Batch upsert committed: {len(results)} records processed total")
            return results
            
        except Exception as e:
            logger.error("Batch upsert failed, rolling back: %s", e)
            self.connection.rollback()
            return []
            
        finally:
            self.connection.autocommit = original_autocommit
