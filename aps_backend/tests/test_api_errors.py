"""API-level tests for error responses, health probes, and scheduler failures."""

from fastapi.testclient import TestClient

import main_backend
from api import crud_routes
from repository import ConflictError, DatabaseError

client = TestClient(main_backend.app, raise_server_exceptions=False)


def _patch_repository(monkeypatch, *, fetch_error=None, delete_count=0):
    class FakeRepository:
        def __init__(self, *args, **kwargs):
            pass

        def fetch_all(self):
            if fetch_error is not None:
                raise fetch_error
            return []

        def delete(self, id_value):
            return delete_count

    monkeypatch.setattr(crud_routes, "Repository", FakeRepository)


def test_conflict_maps_to_409_problem_response(monkeypatch):
    _patch_repository(monkeypatch, fetch_error=ConflictError("duplicate key"))

    response = client.get("/api/v1/resources")

    assert response.status_code == 409
    assert response.headers["content-type"].startswith("application/problem+json")
    body = response.json()
    assert body["type"] == "urn:aps:error:conflict"
    assert body["title"] == "Conflict"
    assert body["instance"] == "/api/v1/resources"


def test_database_error_maps_to_500_without_leaking_details(monkeypatch):
    _patch_repository(monkeypatch, fetch_error=DatabaseError("secret SQL detail"))

    response = client.get("/api/v1/resources")

    assert response.status_code == 500
    body = response.json()
    assert body["type"] == "urn:aps:error:database"
    assert "secret SQL detail" not in body["detail"]


def test_unexpected_error_maps_to_generic_500(monkeypatch):
    _patch_repository(monkeypatch, fetch_error=RuntimeError("boom"))

    response = client.get("/api/v1/resources")

    assert response.status_code == 500
    body = response.json()
    assert body["type"] == "urn:aps:error:internal"
    assert "boom" not in body["detail"]


def test_system_table_is_rejected_before_repository_creation(monkeypatch):
    def explode(*args, **kwargs):
        raise AssertionError("Repository must not be created for a denied table")

    monkeypatch.setattr(crud_routes, "Repository", explode)

    response = client.get("/api/v1/users")

    assert response.status_code == 404
    assert response.json()["type"] == "urn:aps:error:not-found"


def test_missing_query_parameter_uses_validation_problem():
    response = client.put("/api/v1/resources", json={"name": "x"})

    assert response.status_code == 422
    body = response.json()
    assert body["type"] == "urn:aps:error:validation"
    assert body["errors"]


def test_delete_of_missing_row_returns_404(monkeypatch):
    _patch_repository(monkeypatch, delete_count=0)

    response = client.delete("/api/v1/resources?id_value=MISSING")

    assert response.status_code == 404
    assert response.json()["type"] == "urn:aps:error:not-found"


def test_health_and_ready_probes():
    assert client.get("/health").json() == {"status": "ok"}

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, *exc_info):
            return False

        def execute(self, statement):
            self.statement = statement

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

    class FakeManager:
        def get_connection(self):
            return FakeConnection()

        def close_connection(self, connection):
            pass

    main_backend.app.dependency_overrides[main_backend.get_connection_manager] = (
        lambda: FakeManager()
    )
    try:
        response = client.get("/ready")
    finally:
        main_backend.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_ready_returns_503_when_database_is_unavailable():
    class FailingManager:
        def get_connection(self):
            raise RuntimeError("connection refused")

    main_backend.app.dependency_overrides[main_backend.get_connection_manager] = (
        lambda: FailingManager()
    )
    try:
        response = client.get("/ready")
    finally:
        main_backend.app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json()["type"] == "urn:aps:error:unavailable"


def _run_scheduler_with(monkeypatch, pipeline_error):
    class FakeRunsRepository:
        def __init__(self, *args, **kwargs):
            self.updates = []

        def add(self, data):
            return [{"id": 42}]

        def update(self, id_value, data):
            self.updates.append((id_value, data))
            return 1

    monkeypatch.setattr(main_backend, "Repository", FakeRunsRepository)
    monkeypatch.setattr(
        main_backend.ScheduleCreator,
        "run",
        lambda run_id=None: (_ for _ in ()).throw(pipeline_error),
    )


def test_scheduler_infeasibility_returns_422(monkeypatch):
    _run_scheduler_with(monkeypatch, ValueError("FAILED: solver status 3"))

    response = client.post("/run_scheduler")

    assert response.status_code == 422
    body = response.json()
    assert body["type"] == "urn:aps:error:validation"
    assert "Scheduling failed" in body["detail"]


def test_scheduler_unexpected_failure_returns_500(monkeypatch):
    _run_scheduler_with(monkeypatch, RuntimeError("unexpected"))

    response = client.post("/run_scheduler")

    assert response.status_code == 500
    assert response.json()["type"] == "urn:aps:error:internal"
