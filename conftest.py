"""Pytest bootstrap guard.

Running the system-wide ``pytest`` against this repository is a common mistake:
the test modules need the project virtualenv's dependencies. Fail once with an
actionable message instead of emitting six import errors.
"""

import importlib.util

import pytest

_REQUIRED_MODULES = (
    "fastapi",
    "httpx",
    "ortools",
    "psycopg2",
    "pydantic",
    "pydantic_settings",
)
_missing = [
    module for module in _REQUIRED_MODULES if importlib.util.find_spec(module) is None
]

if _missing:
    raise pytest.UsageError(
        "Missing project dependency/dependencies: "
        f"{', '.join(_missing)}.\n"
        "Use the project virtualenv, for example:\n"
        "  .venv/bin/python -m pip install -r aps_backend/requirements.txt -r requirements-dev.txt\n"
        "  .venv/bin/python -m pytest\n"
        "See the 'Running Backend Unit Tests' section in README.md."
    )
