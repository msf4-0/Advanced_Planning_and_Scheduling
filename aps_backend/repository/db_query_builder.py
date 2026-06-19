"""
SQL query builder with parameter binding.
Constructs parameterized SQL queries to prevent injection.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class QueryBuilder:
    """Builds parameterized SQL queries safely."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.filters = []
        self.filter_values = []
        self.order_by_clauses = []
        self.limit_val = None
        self.offset_val = None
    
    def where(self, column: str, value: Any, operator: str = "=") -> "QueryBuilder":
        """
        Add a WHERE condition.
        
        Args:
            column: Column name
            value: Filter value (will be parameterized)
            operator: Comparison operator (=, !=, <, >, <=, >=, LIKE, IN, etc.)
            
        Returns:
            Self for chaining
        """
        self.filters.append((column, operator))
        self.filter_values.append(value)
        return self
    
    def order(self, column: str, direction: str = "ASC") -> "QueryBuilder":
        """
        Add ORDER BY clause.
        
        Args:
            column: Column name
            direction: "ASC" or "DESC"
            
        Returns:
            Self for chaining
        """
        direction = direction.upper()
        if direction not in ("ASC", "DESC"):
            raise ValueError(f"Invalid direction: {direction}")
        self.order_by_clauses.append(f'"{column}" {direction}')
        return self
    
    def limit(self, count: int) -> "QueryBuilder":
        """Set LIMIT clause."""
        if count < 0:
            raise ValueError("Limit must be non-negative")
        self.limit_val = count
        return self
    
    def offset(self, count: int) -> "QueryBuilder":
        """Set OFFSET clause."""
        if count < 0:
            raise ValueError("Offset must be non-negative")
        self.offset_val = count
        return self
    
    def build_select(self, columns: Optional[List[str]] = None) -> Tuple[str, list]:
        """
        Build a SELECT query.
        
        Args:
            columns: Specific columns to select (None = all)
            
        Returns:
            Tuple of (SQL string, parameters list)
        """
        if columns:
            cols = ", ".join(f'"{col}"' for col in columns)
        else:
            cols = "*"
        
        sql = f'SELECT {cols} FROM "{self.table_name}"'
        params = []
        
        if self.filters:
            conditions = [f'"{col}" {op} %s' for col, op in self.filters]
            sql += " WHERE " + " AND ".join(conditions)
            params.extend(self.filter_values)
        
        if self.order_by_clauses:
            sql += " ORDER BY " + ", ".join(self.order_by_clauses)
        
        if self.limit_val is not None:
            sql += f" LIMIT {self.limit_val}"
            if self.offset_val is not None:
                sql += f" OFFSET {self.offset_val}"
        
        sql += ";"
        return sql, params
    
    def build_insert(self, data: Dict[str, Any]) -> Tuple[str, list]:
        """
        Build an INSERT query with RETURNING.
        
        Args:
            data: Column-value dictionary
            
        Returns:
            Tuple of (SQL string, parameters list)
        """
        columns = ", ".join(f'"{col}"' for col in data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        sql = f'INSERT INTO "{self.table_name}" ({columns}) VALUES ({placeholders}) RETURNING *;'
        params = list(data.values())
        return sql, params
    
    def build_update(self, data: Dict[str, Any]) -> Tuple[str, list]:
        """
        Build an UPDATE query.
        
        Args:
            data: Column-value dictionary for SET clause
            
        Returns:
            Tuple of (SQL string, parameters list)
        """
        set_clauses = ", ".join(f'"{col}" = %s' for col in data.keys())
        sql = f'UPDATE "{self.table_name}" SET {set_clauses}'
        params = list(data.values())
        
        if self.filters:
            conditions = [f'"{col}" {op} %s' for col, op in self.filters]
            sql += " WHERE " + " AND ".join(conditions)
            params.extend(self.filter_values)
        
        sql += ";"
        return sql, params
    
    def build_delete(self) -> Tuple[str, list]:
        """
        Build a DELETE query.
        
        Returns:
            Tuple of (SQL string, parameters list)
        """
        sql = f'DELETE FROM "{self.table_name}"'
        params = []
        
        if self.filters:
            conditions = [f'"{col}" {op} %s' for col, op in self.filters]
            sql += " WHERE " + " AND ".join(conditions)
            params.extend(self.filter_values)
        
        sql += ";"
        return sql, params
    
    def build_upsert(self, data: Dict[str, Any], conflict_columns: List[str]) -> Tuple[str, list]:
        """
        Build an UPSERT (INSERT ... ON CONFLICT) query.
        
        Args:
            data: Column-value dictionary
            conflict_columns: Columns that trigger the conflict
            
        Returns:
            Tuple of (SQL string, parameters list)
        """
        columns = ", ".join(f'"{col}"' for col in data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        conflict_cols = ", ".join(f'"{col}"' for col in conflict_columns)
        
        # UPDATE all columns except conflict columns
        update_cols = [col for col in data.keys() if col not in conflict_columns]
        update_clause = ", ".join(f'"{col}" = EXCLUDED."{col}"' for col in update_cols)
        
        sql = f'''INSERT INTO "{self.table_name}" ({columns})
        VALUES ({placeholders})
        ON CONFLICT ({conflict_cols}) DO UPDATE SET {update_clause}
        RETURNING *;'''
        
        params = list(data.values())
        return sql, params
    
    def build_count(self) -> Tuple[str, list]:
        """
        Build a COUNT query.
        
        Returns:
            Tuple of (SQL string, parameters list)
        """
        sql = f'SELECT COUNT(*) FROM "{self.table_name}"'
        params = []
        
        if self.filters:
            conditions = [f'"{col}" {op} %s' for col, op in self.filters]
            sql += " WHERE " + " AND ".join(conditions)
            params.extend(self.filter_values)
        
        sql += ";"
        return sql, params
    
    def reset(self) -> "QueryBuilder":
        """Reset all builder state for reuse."""
        self.filters = []
        self.filter_values = []
        self.order_by_clauses = []
        self.limit_val = None
        self.offset_val = None
        return self
