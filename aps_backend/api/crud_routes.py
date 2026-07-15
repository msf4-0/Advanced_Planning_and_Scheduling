import logging
from fastapi import APIRouter, HTTPException, Body, Query

# Infrastructure Layer
from repository import Repository, DatabaseConfig, ConnectionManager

router = APIRouter(prefix="/api/v1", tags=["Frontend CRUD"])

@router.get("/{table_name}")
def read_all_records(table_name: str):
    """Generic Read: Fetches all flat records from the specified table layout."""
    try:
        config = DatabaseConfig()
        conn_manager = ConnectionManager(config)
        repo = Repository(table_name=table_name, connection_manager=conn_manager)
        
        records = repo.fetch_all()
        return {"success": True, "table": table_name, "count": len(records), "data": records}
    except Exception as e:
        logging.error(f"CRUD Read failure on table '{table_name}': {e}")
        raise HTTPException(status_code=400, detail=f"Failed to fetch data from {table_name}: {str(e)}")


@router.post("/{table_name}")
def create_record(table_name: str, payload: dict = Body(...)):
    """Generic Create: Adds a new record entry to the targeted table schema."""
    try:
        config = DatabaseConfig()
        conn_manager = ConnectionManager(config)
        repo = Repository(table_name=table_name, connection_manager=conn_manager)
        
        repo.add(data=payload)
        return {"success": True, "message": f"Record inserted successfully into {table_name}."}
    except Exception as e:
        logging.error(f"CRUD Create failure on table '{table_name}': {e}")
        raise HTTPException(status_code=400, detail=f"Failed to insert record into {table_name}: {str(e)}")


@router.put("/{table_name}")
def update_record(table_name: str, id_value: str = Query(...), payload: dict = Body(...)):
    """Generic Update: Modifies a row individually matching its primary identifier."""
    try:
        config = DatabaseConfig()
        conn_manager = ConnectionManager(config)
        repo = Repository(table_name=table_name, connection_manager=conn_manager)
        
        repo.update(id_value=id_value, data=payload)
        return {"success": True, "message": f"Record '{id_value}' updated successfully in {table_name}."}
    except Exception as e:
        logging.error(f"CRUD Update failure on table '{table_name}' for ID '{id_value}': {e}")
        raise HTTPException(status_code=400, detail=f"Failed to update record in {table_name}: {str(e)}")


@router.delete("/{table_name}")
def delete_record(table_name: str, id_value: str = Query(...)):
    """Generic Delete: Erases a targeted data row completely out of the database canvas."""
    try:
        config = DatabaseConfig()
        conn_manager = ConnectionManager(config)
        repo = Repository(table_name=table_name, connection_manager=conn_manager)
        
        repo.delete(id_value=id_value)
        return {"success": True, "message": f"Record '{id_value}' dropped cleanly from {table_name}."}
    except Exception as e:
        logging.error(f"CRUD Delete failure on table '{table_name}' for ID '{id_value}': {e}")
        raise HTTPException(status_code=400, detail=f"Failed to delete record from {table_name}: {str(e)}")
