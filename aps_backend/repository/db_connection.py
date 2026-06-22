"""
Database connection management.
Handles connection lifecycle, pooling, and timezone setup.
"""

import os
import psycopg2
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Centralized database configuration from environment variables."""
    
    def __init__(self):
        self.host = os.getenv("POSTGRES_HOST", "postgres")
        self.port = int(os.getenv("POSTGRES_PORT", 5432))
        self.user = os.getenv("POSTGRES_USER", "postgresUser")
        self.password = os.getenv("POSTGRES_PASSWORD", "postgresPass")
        self.dbname = os.getenv("POSTGRES_DB", "postgresDB")
    
    def to_dict(self) -> dict:
        """Convert config to psycopg2 connection params."""
        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "dbname": self.dbname
        }


class ConnectionManager:
    """Manages database connections and their lifecycle."""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
    
    def get_connection(self):
        """
        Get a new database connection with UTC timezone.
        
        Returns:
            psycopg2 connection object
            
        Raises:
            psycopg2.Error: If connection fails
        """
        try:
            conn = psycopg2.connect(**self.config.to_dict())
            # Ensure PostgreSQL session uses UTC
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("SET TIME ZONE 'UTC';")
            return conn
        except psycopg2.Error as e:
            logger.error("Failed to connect to database: %s", e)
            raise
    
    @staticmethod
    def close_connection(conn) -> None:
        """Safely close a connection."""
        if conn:
            try:
                conn.close()
            except Exception as e:
                logger.warning("Error closing connection: %s", e)
