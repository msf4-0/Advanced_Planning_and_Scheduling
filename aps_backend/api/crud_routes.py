"""Typed, allowlisted CRUD routes.

The generic route shape is retained for the current frontend, but table access is
restricted to the application's master-data tables. System tables (`users`,
`scheduling_runs`, `scheduled_tasks`) are deliberately excluded and must be
accessed through dedicated endpoints.
"""

from fastapi import APIRouter, Body, HTTPException, Query

from repository import (
    ConnectionManager,
    DatabaseConfig,
    NotFoundError,
    Repository,
)

router = APIRouter(prefix="/api/v1", tags=["Frontend CRUD"])

ALLOWED_TABLES = frozenset(
    {
        "resources",
        "materials",
        "work_orders",
        "operations",
        "operation_dependencies",
        "operation_materials",
        "factory_shifts",
        "factory_holidays",
        "items",
        "routing_templates",
    }
)


def _repository(table_name: str) -> Repository:
    if table_name not in ALLOWED_TABLES:
        raise HTTPException(status_code=404, detail=f"Unknown table '{table_name}'")
    return Repository(
        table_name=table_name,
        connection_manager=ConnectionManager(DatabaseConfig()),
    )


@router.get("/{table_name}")
def read_all_records(table_name: str):
    """Fetch all records from an allowlisted table."""
    repository = _repository(table_name)
    records = repository.fetch_all()
    return {"success": True, "table": table_name, "count": len(records), "data": records}


@router.post("/{table_name}")
def create_record(table_name: str, payload: dict = Body(...)):
    """Insert a record into an allowlisted table."""
    repository = _repository(table_name)
    repository.add(data=payload)
    return {"success": True, "message": f"Record inserted successfully into {table_name}."}


@router.put("/{table_name}")
def update_record(table_name: str, id_value: str = Query(...), payload: dict = Body(...)):
    """Update a record by its `id` primary key."""
    repository = _repository(table_name)
    updated = repository.update(id_value=id_value, data=payload)
    if updated == 0:
        raise NotFoundError(f"Record '{id_value}' was not found in '{table_name}'.")
    return {"success": True, "message": f"Record '{id_value}' updated successfully in {table_name}."}


@router.delete("/{table_name}")
def delete_record(table_name: str, id_value: str = Query(...)):
    """Delete a record by its `id` primary key."""
    repository = _repository(table_name)
    deleted = repository.delete(id_value=id_value)
    if deleted == 0:
        raise NotFoundError(f"Record '{id_value}' was not found in '{table_name}'.")
    return {"success": True, "message": f"Record '{id_value}' dropped cleanly from {table_name}."}
