"""RFC 7807 problem responses for the APS API.

Every error exits through one of these handlers so clients can rely on a single
response shape::

    {
        "type": "urn:aps:error:conflict",
        "title": "Conflict",
        "status": 409,
        "detail": "...",
        "instance": "/api/v1/resources"
    }

Repository exceptions are mapped by category; database details are logged but
never returned to the client.
"""

import logging
from http import HTTPStatus
from typing import Any, Mapping, Optional

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from repository import (
    ConflictError,
    DatabaseError,
    NotFoundError,
    RepositoryError,
    RepositoryValidationError,
)

logger = logging.getLogger(__name__)

PROBLEM_MEDIA_TYPE = "application/problem+json"

_STATUS_KINDS = {
    400: "bad-request",
    401: "unauthorized",
    403: "forbidden",
    404: "not-found",
    409: "conflict",
    422: "validation",
    500: "internal",
    503: "unavailable",
}


def problem_response(
    request: Request,
    status: int,
    kind: str,
    title: str,
    detail: str,
    *,
    errors: Optional[list[Any]] = None,
    headers: Optional[Mapping[str, str]] = None,
) -> JSONResponse:
    body = {
        "type": f"urn:aps:error:{kind}",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.url.path,
    }
    if errors:
        body["errors"] = errors
    return JSONResponse(
        status_code=status,
        content=body,
        headers=dict(headers) if headers else None,
        media_type=PROBLEM_MEDIA_TYPE,
    )


def _status_title(status: int) -> str:
    try:
        return HTTPStatus(status).phrase
    except ValueError:
        return "Request failed"


def _status_kind(status: int) -> str:
    return _STATUS_KINDS.get(status, "http")


async def repository_error_handler(request: Request, exc: RepositoryError) -> JSONResponse:
    if isinstance(exc, RepositoryValidationError):
        return problem_response(
            request,
            422,
            "validation",
            "Request validation failed",
            str(exc),
        )
    if isinstance(exc, NotFoundError):
        return problem_response(request, 404, "not-found", "Not Found", str(exc))
    if isinstance(exc, ConflictError):
        return problem_response(request, 409, "conflict", "Conflict", str(exc))

    if isinstance(exc, DatabaseError):
        logger.error("Database error on %s: %s", request.url.path, exc)
        return problem_response(
            request,
            500,
            "database",
            "Database operation failed",
            "A database error occurred while processing the request.",
        )

    logger.error("Repository error on %s: %s", request.url.path, exc)
    return problem_response(
        request,
        500,
        "internal",
        "Internal server error",
        "An unexpected repository error occurred.",
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else jsonable_encoder(exc.detail)
    return problem_response(
        request,
        exc.status_code,
        _status_kind(exc.status_code),
        _status_title(exc.status_code),
        detail or _status_title(exc.status_code),
        headers=exc.headers,
    )


async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = [
        {key: value for key, value in error.items() if key != "ctx"}
        for error in exc.errors()
    ]
    return problem_response(
        request,
        422,
        "validation",
        "Request validation failed",
        "One or more request fields are invalid.",
        errors=jsonable_encoder(errors),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Unhandled exception on %s",
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return problem_response(
        request,
        500,
        "internal",
        "Internal server error",
        "An unexpected error occurred while processing the request.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach the RFC 7807 handlers to the application."""
    app.add_exception_handler(RepositoryError, repository_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
