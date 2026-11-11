"""APS FastAPI application.

`app.main` is the canonical entry point (`uvicorn app.main:app`).
"""

import logging
from datetime import datetime

import uvicorn
from fastapi import Depends, FastAPI, HTTPException

from api import crud_routes
from api.errors import register_exception_handlers
from app.config import Settings, get_settings
from app.domain.enums import RunStatus
from classes import ScheduleCreator
from repository import (
    ConnectionManager,
    DatabaseConfig,
    Repository,
    RepositoryError,
)

app = FastAPI(title="APS Production Scheduling Engine API")
logging.basicConfig(level=get_settings().log_level)

register_exception_handlers(app)
app.include_router(crud_routes.router)


def _database_config(settings: Settings) -> DatabaseConfig:
    return DatabaseConfig(**settings.database_kwargs())


def get_connection_manager(
    settings: Settings = Depends(get_settings),
) -> ConnectionManager:
    """Dependency so tests can override database connectivity."""
    return ConnectionManager(_database_config(settings))


def _mark_run_failed(runs_repo: Repository, run_id, error: Exception) -> None:
    if not run_id:
        return
    try:
        runs_repo.update(
            run_id,
            {
                "run_status": RunStatus.FAILED.value,
                "completed_at": datetime.now(),
                "log_messages": f"Pipeline failed with error: {error}",
            },
        )
    except Exception:
        logging.exception("(API) Could not update run %s to Failed", run_id)


@app.get("/health", tags=["Health"])
def health():
    """Liveness probe: the process is up and serving requests."""
    return {"status": "ok"}


@app.get("/ready", tags=["Health"])
def ready(conn_manager: ConnectionManager = Depends(get_connection_manager)):
    """Readiness probe: the API can reach PostgreSQL."""
    connection = None
    try:
        connection = conn_manager.get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return {"status": "ready"}
    except Exception as exc:
        logging.warning("(API) Readiness check failed: %s", exc)
        raise HTTPException(status_code=503, detail="Database is not ready") from exc
    finally:
        if connection is not None:
            conn_manager.close_connection(connection)


@app.post("/run_scheduler", tags=["Schedule"])
def run_scheduler_endpoint():
    """
    Register a run, execute the ScheduleCreator pipeline, and return the result.

    Pipeline failures are non-2xx: solver infeasibility is 422, repository
    failures keep their typed status, and unexpected failures are 500.
    """
    config = _database_config(get_settings())
    conn_manager = ConnectionManager(config)
    runs_repo = Repository("scheduling_runs", conn_manager)

    active_run_id = None

    # 1. Register the run. A logging failure is non-fatal; the scheduler can
    # still produce a result and write its own audit row.
    try:
        logging.info("(API) Registering pipeline optimization run tracking entry...")
        new_run_list = runs_repo.add(
            data={
                "run_status": RunStatus.RUNNING.value,
                "started_at": datetime.now(),
                "log_messages": "Optimization workflow initiated via API request endpoint.",
            }
        )
        if new_run_list:
            inserted_row = new_run_list[0]
            if isinstance(inserted_row, dict):
                active_run_id = inserted_row.get("id")
                logging.info(
                    "(API) Run tracked successfully. Generated Run ID: %s",
                    active_run_id,
                )
    except Exception as log_err:
        logging.warning(
            "(API) Non-fatal audit log tracking registration failure: %s", log_err
        )

    # 2. Execute the pipeline and map failures to HTTP status codes.
    try:
        logging.info("(API) Triggering scheduling creation pipeline...")
        result = ScheduleCreator.run(run_id=active_run_id)
        return {"success": True, "result": result}

    except ValueError as pipeline_err:
        logging.error("(API) Scheduling infeasibility: %s", pipeline_err)
        _mark_run_failed(runs_repo, active_run_id, pipeline_err)
        raise HTTPException(
            status_code=422,
            detail=f"Scheduling failed: {pipeline_err}",
        ) from pipeline_err

    except RepositoryError as pipeline_err:
        _mark_run_failed(runs_repo, active_run_id, pipeline_err)
        raise

    except Exception as pipeline_err:
        logging.exception("(API) Critical failure in pipeline execution")
        _mark_run_failed(runs_repo, active_run_id, pipeline_err)
        raise HTTPException(
            status_code=500,
            detail="Scheduling pipeline failed unexpectedly.",
        ) from pipeline_err


@app.get("/recent-schedule", tags=["Schedule"])
def get_schedule():
    """
    Return the most recent successful run and its scheduled-task snapshots.
    """
    config = _database_config(get_settings())
    conn_manager = ConnectionManager(config)

    runs_repo = Repository("scheduling_runs", conn_manager)
    tasks_repo = Repository("scheduled_tasks", conn_manager)

    all_runs = runs_repo.fetch_all()
    successful_runs = [
        run for run in all_runs if run.get("run_status") == RunStatus.SUCCESS.value
    ]

    if not successful_runs:
        return {
            "success": True,
            "message": "No successful schedule runs found yet.",
            "run_info": {},
            "tasks": [],
        }

    latest_run = max(successful_runs, key=lambda run: run.get("id") or 0)
    run_id = latest_run.get("id")

    all_tasks = tasks_repo.fetch_all()
    latest_tasks = [task for task in all_tasks if task.get("run_id") == run_id]

    return {
        "success": True,
        "run_info": latest_run,
        "tasks": latest_tasks,
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
