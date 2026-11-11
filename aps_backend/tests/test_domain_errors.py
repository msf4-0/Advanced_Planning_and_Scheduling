"""Tests for the domain error hierarchy and its repository subclasses."""

from app.domain import errors as domain
from repository import errors as repository


def test_all_expected_errors_are_domain_errors():
    for error_type in (
        domain.ValidationError,
        domain.NotFoundError,
        domain.ConflictError,
        domain.InfeasibleSchedule,
        domain.SchedulerUnavailable,
    ):
        assert issubclass(error_type, domain.DomainError)


def test_repository_errors_are_domain_errors():
    assert issubclass(repository.RepositoryError, domain.DomainError)
    assert issubclass(repository.RepositoryValidationError, domain.ValidationError)
    assert issubclass(repository.NotFoundError, domain.NotFoundError)
    assert issubclass(repository.ConflictError, domain.ConflictError)
    assert issubclass(repository.DatabaseError, domain.DomainError)
