from fastapi import APIRouter, Body, HTTPException, Query, UploadFile, File
from typing_extensions import List
from typing import Dict

from repository import DBTable
from schema_mapper import SchemaMapper

import logging
import csv

router = APIRouter()



@router.get(
    "/data",
    response_model=List[Dict],
    tags=["Table General"]
)
def get_table_data(
    table_name: str = Query(...),
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
    Accepts either a filepath (str) or a file object.
    Returns a dictionary with section names as keys and list of row dicts as values.
    """

    db = DBTable()
    data = {}

    try:
        contents = await csv_file.read()
        decoded = contents.decode("utf-8").splitlines()
        reader = csv.DictReader(decoded)
        logging.info(f"Importing data into table: {table_name}")
        logging.info(f"CSV Headers: {reader.fieldnames}")
        # Read all rows into a list so we can use it multiple times
        raw_rows = list(reader)
        logging.info(f"Number of rows to import: {len(raw_rows)}")
        all_rows = []
        for row in raw_rows:
            clean_row = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
            db.add(table_name, clean_row)
            all_rows.append(clean_row)
        
        if not all_rows:
            logging.warning("No rows were imported from the CSV file.")
            raise HTTPException(status_code=200, detail="No data imported from CSV file.")
        
        return {"imported": len(all_rows), "rows": all_rows}
    except Exception as e:
        logging.error(f"Error parsing CSV file: {e}")
        return {"error": str(e)}