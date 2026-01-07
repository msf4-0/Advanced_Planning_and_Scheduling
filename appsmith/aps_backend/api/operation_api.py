from fastapi import APIRouter, Body, HTTPException
from typing_extensions import List, Optional
from repository import DBTable
from models import OperationRead
from service import OperationService

router = APIRouter()

@router.get(
        "/get/operations", 
        response_model=List[OperationRead],
        tags=["Operations"]
        )
def get_operations():
    '''
    Fetch the list of operations from the database.
    
    Location: appsmith/aps_backend/api/operation_api.py
    '''

    db = DBTable()
    rows = db.fetch_operations()
    operations = [
        OperationRead(
            operation_id=row['operation_id'],
            name=row['name'],
            duration=row['duration'],
            machine_type=row['type_id'],
            material_id=row.get('material_id')
        )
        for row in rows
    ]

    return operations

@router.post(
        "/add/operation", 
        response_model=OperationRead, 
        status_code=201,
        tags=["Operations"]
        )
def add_operation(
    name: str = Body(...), 
    required_machine_type: str = Body(...), 
    duration: int = Body(...), 
    material_needed: Optional[str] = Body(None)
    ):
    '''
    Add a new operation to the system.

    Location: appsmith/aps_backend/api/operation_api.py
    '''

    operation_service = OperationService(DBTable())
    
    operation = operation_service.add_operation(
        name=name,
        required_machine_type=required_machine_type,
        duration=duration,
        material_needed=material_needed
    )
    
    if operation is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Failed to create operation.")
    
    return operation

@router.post(
        "/generate/opnode/{operation_id}",
        status_code=201,
        tags=["Operations"]
        )
def generate_operation_node(operation_id: int):
    '''
    Generate an operation node for the given operation ID.
    Location: appsmith/aps_backend/api/operation_api.py
    '''

    operation_service = OperationService(DBTable())

    try:
        operation_service.generate_operation_node(operation_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"status": "operation node generated"}