"""Typed exceptions raised by the repository layer.

Callers must not receive ambiguous defaults (``[]``, ``None``, ``0``) for a
failed database operation. The HTTP layer maps these exceptions to status codes
in Phase 0 item 7; until then the generic CRUD routes surface them as 400.
"""


class RepositoryError(Exception):
    """Base class for all repository-layer failures."""


class RepositoryValidationError(RepositoryError):
    """Input failed table/column/value validation before SQL was executed."""


class NotFoundError(RepositoryError):
    """A requested record does not exist. Reserved for the typed API layer."""


class ConflictError(RepositoryError):
    """The write violated a database constraint (unique, FK, NOT NULL, check)."""


class DatabaseError(RepositoryError):
    """The database rejected or could not execute the operation."""
