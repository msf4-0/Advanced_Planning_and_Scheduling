"""
Query execution layer.
Handles SQL execution, result fetching, and cursor lifecycle.
"""

import logging
from typing import Any, Dict, List, Optional
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class QueryExecutor:
    """Executes database queries and handles results."""
    
    def __init__(self, connection):
        """
        Initialize executor with a database connection.
        
        Args:
            connection: psycopg2 connection object
        """
        self.connection = connection
    
    def fetch_one(self, sql: str, params: List[Any]) -> Optional[Dict[str, Any]]:
        """
        Execute query and fetch first row as dictionary.
        
        Args:
            sql: SQL query string (with %s placeholders)
            params: List of parameter values
            
        Returns:
            Dict of first row, or None if no rows
            
        Raises:
            Exception: If query execution fails
        """
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(sql, params)
            return cursor.fetchone()
        except Exception as e:
            logger.error("Error executing query: %s\nSQL: %s", e, sql)
            raise
        finally:
            cursor.close()
    
    def fetch_many(self, sql: str, params: List[Any]) -> List[Dict[str, Any]]:
        """
        Execute query and fetch all rows as list of dictionaries.
        
        Args:
            sql: SQL query string (with %s placeholders)
            params: List of parameter values
            
        Returns:
            List of dicts (rows)
            
        Raises:
            Exception: If query execution fails
        """
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(sql, params)
            return cursor.fetchall()
        except Exception as e:
            logger.error("Error executing query: %s\nSQL: %s", e, sql)
            raise
        finally:
            cursor.close()
    
    def execute_update(self, sql: str, params: List[Any]) -> int:
        """
        Execute INSERT/UPDATE/DELETE query.
        
        Args:
            sql: SQL query string (with %s placeholders)
            params: List of parameter values
            
        Returns:
            Number of rows affected
            
        Raises:
            Exception: If query execution fails
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, params)
            affected_rows = cursor.rowcount
            self.connection.commit()
            logger.debug("Query affected %d rows", affected_rows)
            return affected_rows
        except Exception as e:
            self.connection.rollback()
            logger.error("Error executing update: %s\nSQL: %s", e, sql)
            raise
        finally:
            cursor.close()
    
    def execute_insert_returning(self, sql: str, params: List[Any]) -> List[Dict[str, Any]]:
        """
        Execute INSERT with RETURNING clause.
        
        Args:
            sql: SQL query string (with %s placeholders)
            params: List of parameter values
            
        Returns:
            List of inserted rows
            
        Raises:
            Exception: If query execution fails
        """
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            self.connection.commit()
            logger.debug("Inserted %d rows", len(rows))
            return rows
        except Exception as e:
            self.connection.rollback()
            logger.error("Error executing insert: %s\nSQL: %s", e, sql)
            raise
        finally:
            cursor.close()
    
    def execute_scalar(self, sql: str, params: List[Any]) -> Optional[Any]:
        """
        Execute query and fetch scalar value (first column of first row).
        Used for COUNT, MAX, etc.
        
        Args:
            sql: SQL query string (with %s placeholders)
            params: List of parameter values
            
        Returns:
            Scalar value or None
            
        Raises:
            Exception: If query execution fails
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, params)
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            logger.error("Error executing scalar query: %s\nSQL: %s", e, sql)
            raise
        finally:
            cursor.close()
