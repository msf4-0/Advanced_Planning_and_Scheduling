from fastapi import APIRouter, Body, HTTPException, Query
from typing_extensions import List
from typing import Dict

from repository import DBTable, GraphEditor
from schema_mapper import SchemaMapper

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
