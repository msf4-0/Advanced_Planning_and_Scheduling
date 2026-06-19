"""
Input validation and sanitization for database operations.
Provides guardrails against SQL injection and invalid data.
"""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class InputValidator:
    """Validates and sanitizes user inputs before database operations."""
    
    # Allowed characters for table and column names
    IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
    
    # Reserved SQL keywords that should not be table names
    RESERVED_KEYWORDS = {
        'select', 'insert', 'update', 'delete', 'from', 'where',
        'join', 'on', 'group', 'order', 'limit', 'offset',
        'create', 'alter', 'drop', 'table', 'column', 'constraint'
    }
    
    @staticmethod
    def validate_table_name(table_name: str, allowed_tables: Optional[List[str]] = None) -> None:
        """
        Validate that a table name is safe and allowed.
        
        Args:
            table_name: The table name to validate
            allowed_tables: Optional whitelist of allowed table names
            
        Raises:
            ValueError: If table name is invalid or not in whitelist
        """
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Table name must be a non-empty string")
        
        # Check length
        if len(table_name) > 63:  # PostgreSQL identifier limit
            raise ValueError(f"Table name too long (max 63 characters): {table_name}")
        
        # Check pattern
        if not InputValidator.IDENTIFIER_PATTERN.match(table_name):
            raise ValueError(
                f"Invalid table name '{table_name}'. "
                "Must start with letter or underscore, contain only alphanumeric and underscores"
            )
        
        # Check against reserved keywords
        if table_name.lower() in InputValidator.RESERVED_KEYWORDS:
            raise ValueError(f"Table name '{table_name}' is a reserved SQL keyword")
        
        # Check whitelist if provided
        if allowed_tables and table_name not in allowed_tables:
            raise ValueError(f"Table '{table_name}' not in allowed table list")
    
    @staticmethod
    def validate_column_name(column_name: str) -> None:
        """
        Validate that a column name is safe.
        
        Args:
            column_name: The column name to validate
            
        Raises:
            ValueError: If column name is invalid
        """
        if not column_name or not isinstance(column_name, str):
            raise ValueError("Column name must be a non-empty string")
        
        if len(column_name) > 63:
            raise ValueError(f"Column name too long (max 63 characters): {column_name}")
        
        if not InputValidator.IDENTIFIER_PATTERN.match(column_name):
            raise ValueError(
                f"Invalid column name '{column_name}'. "
                "Must start with letter or underscore, contain only alphanumeric and underscores"
            )
    
    @staticmethod
    def validate_dict(data: Dict[str, Any], allow_empty: bool = False) -> None:
        """
        Validate that a dictionary is safe for database operations.
        
        Args:
            data: The dictionary to validate (column-value pairs)
            allow_empty: Whether to allow empty dictionaries
            
        Raises:
            ValueError: If dictionary is invalid
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        if not allow_empty and not data:
            raise ValueError("Data dictionary cannot be empty")
        
        for key in data.keys():
            InputValidator.validate_column_name(key)
    
    @staticmethod
    def validate_conditions(conditions: Optional[Dict[str, Any]]) -> None:
        """
        Validate filter conditions dictionary.
        
        Args:
            conditions: The conditions dictionary to validate
            
        Raises:
            ValueError: If conditions are invalid
        """
        if conditions is None:
            return
        
        if not isinstance(conditions, dict):
            raise ValueError("Conditions must be a dictionary")
        
        for key in conditions.keys():
            InputValidator.validate_column_name(key)
    
    @staticmethod
    def validate_conflict_columns(conflict_columns: List[str]) -> None:
        """
        Validate conflict columns list for upsert operations.
        
        Args:
            conflict_columns: List of column names
            
        Raises:
            ValueError: If conflict columns are invalid
        """
        if not conflict_columns or not isinstance(conflict_columns, list):
            raise ValueError("Conflict columns must be a non-empty list")
        
        for col in conflict_columns:
            InputValidator.validate_column_name(col)


class InputSanitizer:
    """Sanitizes data values for safe insertion."""
    
    @staticmethod
    def sanitize_value(value: Any) -> Any:
        """
        Sanitize a single value for database insertion.
        Note: This is defensive. Parameterized queries are the primary defense.
        
        Args:
            value: The value to sanitize
            
        Returns:
            The sanitized value
        """
        # Allow None/NULL
        if value is None:
            return None
        
        # Allow numbers, booleans, bytes as-is
        if isinstance(value, (int, float, bool, bytes)):
            return value
        
        # Strings: basic length check
        if isinstance(value, str):
            if len(value) > 1_000_000:  # 1MB limit for strings
                raise ValueError("String value exceeds maximum length (1MB)")
            return value
        
        # Allow datetime objects (psycopg2 handles conversion)
        try:
            from datetime import datetime, date, time
            if isinstance(value, (datetime, date, time)):
                return value
        except ImportError:
            pass
        
        # For everything else, convert to string
        return str(value)
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize all values in a dictionary.
        
        Args:
            data: The dictionary to sanitize
            
        Returns:
            Dictionary with sanitized values
        """
        return {key: InputSanitizer.sanitize_value(val) for key, val in data.items()}


class ValidationPipeline:
    """Combined validation and sanitization pipeline."""
    
    @staticmethod
    def validate_and_sanitize_fetch(
        table_name: str,
        params: Optional[Dict[str, Any]] = None,
        allowed_tables: Optional[List[str]] = None
    ) -> tuple[str, Dict[str, Any]]:
        """
        Validate and sanitize inputs for fetch operations.
        
        Args:
            table_name: Table name to validate
            params: Filter parameters to validate
            allowed_tables: Whitelist of allowed tables
            
        Returns:
            Tuple of (validated_table_name, sanitized_params)
            
        Raises:
            ValueError: If any validation fails
        """
        InputValidator.validate_table_name(table_name, allowed_tables)
        InputValidator.validate_conditions(params)
        
        sanitized_params = InputSanitizer.sanitize_dict(params) if params else {}
        return table_name, sanitized_params
    
    @staticmethod
    def validate_and_sanitize_add(
        table_name: str,
        data: Dict[str, Any],
        allowed_tables: Optional[List[str]] = None
    ) -> tuple[str, Dict[str, Any]]:
        """
        Validate and sanitize inputs for add/insert operations.
        
        Args:
            table_name: Table name to validate
            data: Record data to validate and sanitize
            allowed_tables: Whitelist of allowed tables
            
        Returns:
            Tuple of (validated_table_name, sanitized_data)
            
        Raises:
            ValueError: If any validation fails
        """
        InputValidator.validate_table_name(table_name, allowed_tables)
        InputValidator.validate_dict(data, allow_empty=False)
        
        sanitized_data = InputSanitizer.sanitize_dict(data)
        return table_name, sanitized_data
    
    @staticmethod
    def validate_and_sanitize_update(
        table_name: str,
        data: Dict[str, Any],
        conditions: Dict[str, Any],
        allowed_tables: Optional[List[str]] = None
    ) -> tuple[str, Dict[str, Any], Dict[str, Any]]:
        """
        Validate and sanitize inputs for update operations.
        
        Args:
            table_name: Table name to validate
            data: Update data
            conditions: Filter conditions
            allowed_tables: Whitelist of allowed tables
            
        Returns:
            Tuple of (validated_table_name, sanitized_data, sanitized_conditions)
            
        Raises:
            ValueError: If any validation fails
        """
        InputValidator.validate_table_name(table_name, allowed_tables)
        InputValidator.validate_dict(data, allow_empty=False)
        InputValidator.validate_conditions(conditions)
        
        sanitized_data = InputSanitizer.sanitize_dict(data)
        sanitized_conditions = InputSanitizer.sanitize_dict(conditions) if conditions else {}
        
        return table_name, sanitized_data, sanitized_conditions