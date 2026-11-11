"""Tests for the repository error contract.

These tests do not need a database: the query executor and connection manager
are replaced with mocks, and the tests assert that failures become typed
repository exceptions instead of ambiguous empty returns.
"""

from unittest.mock import MagicMock

import psycopg2
import pytest

from repository import (
    ConflictError,
    DatabaseError,
    Repository,
    RepositoryValidationError,
)


def make_repository(table_name: str = "resources") -> Repository:
    connection_manager = MagicMock()
    connection_manager.get_connection.return_value = MagicMock()
    return Repository(table_name=table_name, connection_manager=connection_manager)


class UniqueViolationError(Exception):
    """Stand-in for a psycopg2 error carrying a PostgreSQL SQLSTATE code."""

    pgcode = "23505"


def test_add_maps_unique_violation_to_conflict_error():
    repository = make_repository()
    repository.executor.execute_insert_returning = MagicMock(
        side_effect=UniqueViolationError("duplicate key value")
    )

    with pytest.raises(ConflictError, match="inserting into 'resources'"):
        repository.add({"id": "MCH-1", "name": "Machine 1"})


def test_fetch_all_maps_database_failure_to_database_error():
    repository = make_repository()
    repository.executor.fetch_many = MagicMock(
        side_effect=psycopg2.OperationalError("connection lost")
    )

    with pytest.raises(DatabaseError, match="fetching all records from 'resources'"):
        repository.fetch_all()


def test_add_rejects_empty_payload_as_validation_error():
    repository = make_repository()
    repository.executor = MagicMock()

    with pytest.raises(RepositoryValidationError):
        repository.add({})

    repository.executor.execute_insert_returning.assert_not_called()
