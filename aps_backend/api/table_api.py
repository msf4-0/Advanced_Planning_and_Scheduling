from fastapi import APIRouter, Body, HTTPException, Query, UploadFile, File
from typing import List, Dict, Any

from repository import DBTable
from schema_mapper import SchemaMapper

import logging
import csv

router = APIRouter()

@router.get(
    "/recent-schedule",
    response_model=Dict,
    tags=["Table General"]
)
def get_recent_schedule():
    '''
    Fetch the most recent schedule result from the database.
    Directly queries the 'schedule_result' table defined in the SQL schema.
    '''
    db = DBTable()
    try:
        # Fetch data from the schedule_result table
        results = db.fetch("schedule_result")
        
        if not results:
            return {"success": False, "message": "No schedule results found in the database."}

        # Find the latest entry based on created_at or id (descending)
        # This ensures the 'Actual DB' content is reflected in the UI
        sorted_results = sorted(results, key=lambda x: (x.get('created_at') or '', x.get('id', 0)), reverse=True)
        latest = sorted_results[0]
        
        # Ensure the stored JSON string in the `result` column is returned as a dict
        if latest and isinstance(latest, dict) and "result" in latest:
            try:
                # If it's a JSON string stored in the DB, convert to native structure
                if isinstance(latest["result"], (str, bytes)):
                    import json as _json
                    latest["result"] = _json.loads(latest["result"])
            except Exception:
                # Fall back to original value if parsing fails
                pass

        # Structure matches the frontend expectation: data.result.result
        return {"success": True, "result": latest}
    except Exception as e:
        logging.error(f"Error pulling recent schedule from DB: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get(
    "/data",
    response_model=List[Dict],
    tags=["Table General"]
)
def get_table_data(
    table_name: str = Query(...),
    limit: int = Query(100, ge=1),
    offset: int = Query(0, ge=0)
):
    '''
    Fetch data from a specified table with pagination.

    Location: appsmith/aps_backend/api/table_api.py
    '''

    db = DBTable()
    mapper = SchemaMapper(db.get_connection_graph())

    valid_tables = mapper.list_tables()
    try:
        data = db.fetch(table_name, table_list=valid_tables)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.put(
    "/data",
    response_model=List[Dict],
    tags=["Table General"]
)
def add_table_data(
    table_name: str = Query(...),
    record: Dict = Body(...)
):
    '''
    Insert a new record into a specified table.

    Location: appsmith/aps_backend/api/table_api.py
    '''

    db = DBTable()
    mapper = SchemaMapper(db.get_connection_graph())

    valid_tables = mapper.list_tables()
    try:
        result = db.add(
            table_name, 
            record, 
            table_list=valid_tables
            )
        if not result:
            raise HTTPException(status_code=500, detail=f"Failed to insert record into {table_name}.")
        return [dict(row) if not isinstance(row, dict) else row for row in result]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post(
    "/upsert",
    response_model=Dict,
    tags=["Table General"]
)
def upsert_table_data(
    table_name: str = Query(...),
    record: Dict = Body(...),
    conflict_columns: List[str] = Body(...)
):
    '''
    Upsert a record into a specified table based on conflict columns.

    Location: appsmith/aps_backend/api/table_api.py
    '''

    db = DBTable()
    mapper = SchemaMapper(db.get_connection_graph())

    valid_tables = mapper.list_tables()
    try:
        result = db.upsert(
            table_name, 
            record, 
            conflict_columns, 
            table_list=valid_tables
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post(
    "/update",
    response_model=int,
    tags=["Table General"]
)
def update_table_data(
    table_name: str = Query(...),
    condition: dict = Body(...),
    update_values: dict = Body(...)
):
    '''
    Update records in a specified table based on a condition.

    Location: appsmith/aps_backend/api/table_api.py
    '''

    db = DBTable()
    mapper = SchemaMapper(db.get_connection_graph())

    valid_tables = mapper.list_tables()
    try:
        if not condition:
            raise HTTPException(status_code=400, detail="Condition for update cannot be empty.")

        result = db.update(table_name, update_values, condition, table_list=valid_tables)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete(
    "/data",
    response_model=int,
    tags=["Table General"]
)
def delete_table_data(
    table_name: str = Query(...),
    condition: dict = Body(...),
):
    '''
    Delete a record from a specified table based on a condition.

    Location: appsmith/aps_backend/api/table_api.py
    '''

    db = DBTable()
    mapper = SchemaMapper(db.get_connection_graph())

    valid_tables = mapper.list_tables()
    try:
        if not condition:
            raise HTTPException(status_code=400, detail="Condition for deletion cannot be empty.")

        result = db.delete(table_name, condition, table_list=valid_tables)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/import-csv/{table_name}",
    response_model=Dict,
    tags=["Admin"]
)
async def import_csv(table_name: str, csv_file: UploadFile = File(...)):
    """
    Parse CSV file and import data into the specified table.
    Validates the table name against the DB schema and handles data insertion.
    """

    db = DBTable()
    mapper = SchemaMapper(db.get_connection_graph())
    valid_tables = mapper.list_tables()

    if table_name not in valid_tables:
        raise HTTPException(status_code=400, detail=f"Table '{table_name}' does not exist or is restricted.")

    try:
        contents = await csv_file.read()
        # Use utf-8-sig to correctly handle Byte Order Marks (BOM) from Excel exports
        decoded = contents.decode("utf-8-sig").splitlines()
        reader = csv.DictReader(decoded)
        
        logging.info(f"Importing data into table: {table_name}")
        logging.info(f"CSV Headers: {reader.fieldnames}")

        raw_rows = list(reader)
        logging.info(f"Number of rows to import: {len(raw_rows)}")
        
        all_rows = []
        for row in raw_rows:
            # Strip whitespace and normalize values
            clean_row = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
            result = db.add(table_name, clean_row, table_list=valid_tables)
            
            # Capture the actual DB record (including auto-generated IDs/timestamps)
            if result and isinstance(result, list) and len(result) > 0:
                all_rows.append(result[0])
            else:
                all_rows.append(clean_row)
        
        if not all_rows:
            logging.warning("No rows were imported from the CSV file.")
            raise HTTPException(status_code=200, detail="No data imported from CSV file.")
        
        return {"imported": len(all_rows), "rows": all_rows}
    except Exception as e:
        logging.error(f"Error parsing CSV file: {e}")
        raise HTTPException(status_code=500, detail=str(e))