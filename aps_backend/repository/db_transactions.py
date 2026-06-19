"""
Transaction management.
Handles database transactions, savepoints, and rollback logic.
"""

import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class TransactionManager:
    """Manages database transactions and savepoints."""
    
    def __init__(self, connection):
        """
        Initialize transaction manager.
        
        Args:
            connection: psycopg2 connection object
        """
        self.connection = connection
        self.in_transaction = False
    
    def begin(self) -> None:
        """Start an explicit transaction."""
        if not self.in_transaction:
            self.connection.autocommit = False
            self.in_transaction = True
            logger.debug("Transaction started")
    
    def commit(self) -> None:
        """Commit the current transaction."""
        if self.in_transaction:
            try:
                self.connection.commit()
                self.in_transaction = False
                logger.debug("Transaction committed")
            except Exception as e:
                logger.error("Error committing transaction: %s", e)
                raise
    
    def rollback(self) -> None:
        """Rollback the current transaction."""
        if self.in_transaction:
            try:
                self.connection.rollback()
                self.in_transaction = False
                logger.debug("Transaction rolled back")
            except Exception as e:
                logger.error("Error rolling back transaction: %s", e)
                raise
    
    def savepoint(self, name: str) -> None:
        """
        Create a named savepoint for nested transaction-like behavior.
        
        Args:
            name: Name of the savepoint (alphanumeric + underscore only)
            
        Raises:
            ValueError: If name is invalid
        """
        if not name or not name.replace('_', '').isalnum():
            raise ValueError(f"Invalid savepoint name: {name}")
        
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"SAVEPOINT {name};")
            logger.debug("Savepoint '%s' created", name)
        except Exception as e:
            logger.error("Error creating savepoint %s: %s", name, e)
            raise
        finally:
            cursor.close()
    
    def rollback_to_savepoint(self, name: str) -> None:
        """
        Rollback to a named savepoint.
        
        Args:
            name: Name of the savepoint
            
        Raises:
            ValueError: If name is invalid
        """
        if not name or not name.replace('_', '').isalnum():
            raise ValueError(f"Invalid savepoint name: {name}")
        
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"ROLLBACK TO SAVEPOINT {name};")
            logger.debug("Rolled back to savepoint '%s'", name)
        except Exception as e:
            logger.error("Error rolling back to savepoint %s: %s", name, e)
            raise
        finally:
            cursor.close()
    
    def release_savepoint(self, name: str) -> None:
        """
        Release (finalize) a named savepoint.
        
        Args:
            name: Name of the savepoint
            
        Raises:
            ValueError: If name is invalid
        """
        if not name or not name.replace('_', '').isalnum():
            raise ValueError(f"Invalid savepoint name: {name}")
        
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"RELEASE SAVEPOINT {name};")
            logger.debug("Savepoint '%s' released", name)
        except Exception as e:
            logger.error("Error releasing savepoint %s: %s", name, e)
            raise
        finally:
            cursor.close()
    
    def __enter__(self):
        """Context manager entry."""
        self.begin()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit — commit or rollback based on exception."""
        if exc_type is not None:
            # Exception occurred, rollback
            self.rollback()
            logger.warning("Transaction rolled back due to exception: %s", exc_type.__name__)
        else:
            # No exception, commit
            self.commit()
    
    @contextmanager
    def savepoint_context(self, name: str):
        """
        Context manager for savepoint-based nested transactions.
        
        Usage:
            with tx_manager.savepoint_context('my_savepoint'):
                # do work
        """
        try:
            self.savepoint(name)
            yield
            self.release_savepoint(name)
        except Exception as e:
            self.rollback_to_savepoint(name)
            logger.warning("Rolled back to savepoint due to exception: %s", e)
            raise
