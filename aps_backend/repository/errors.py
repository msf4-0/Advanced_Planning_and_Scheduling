"""Typed exceptions raised by the repository layer.

Callers must not receive ambiguous defaults (``[]``, ``None``, ``0``) for a
failed database operation. Repository errors subclass the matching domain
errors so API mapping can catch either layer.
"""

from app.domain.errors import (
    ConflictError as DomainConflictError,
    DomainError,
    NotFoundError as DomainNotFoundError,
    ValidationError as DomainValidationError,
)


class RepositoryError(DomainError):
    """Base class for all repository-layer failures."""


class RepositoryValidationError(DomainValidationError, RepositoryError):
    """Input failed table/column/value validation before SQL was executed."""


class NotFoundError(DomainNotFoundError, RepositoryError):
    """A requested record does not exist."""


class ConflictError(DomainConflictError, RepositoryError):
    """The write violated a database constraint (unique, FK, NOT NULL, check)."""


class DatabaseError(RepositoryError):
    """The database rejected or could not execute the operation."""
