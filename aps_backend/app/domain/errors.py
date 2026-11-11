"""Domain-level error hierarchy.

These errors are independent of HTTP and database libraries. The API layer maps
them to RFC 7807 responses; adapters may subclass them for transport-specific
failures (the repository does this for validation/conflict/not-found).
"""


class DomainError(Exception):
    """Base class for expected domain failures."""


class ValidationError(DomainError):
    """A domain value or request violates a business rule."""


class NotFoundError(DomainError):
    """A requested domain object does not exist."""


class ConflictError(DomainError):
    """A domain operation conflicts with existing state."""


class InfeasibleSchedule(DomainError):
    """No schedule satisfies the active constraints and policy."""


class SchedulerUnavailable(DomainError):
    """The scheduling engine or its dependencies are temporarily unavailable."""
