from fastapi import APIRouter, Body
from typing import List, Optional

from repository.db_repository import DBTable
from models import OperationRead
from service import OperationService

router = APIRouter()

@router.get("/get/operations", response_model=List[OperationRead])
def get_operations():
    db = DBTable()
    rows = db.fetch_operations()
    operations = [
        OperationRead(
            operation_id=row['operation_id'],
            name=row['operation_name'],
            duration=row['duration'],
            machine_type=row['machine_type'],
            material_id=row.get('material_id')
        )
        for row in rows
    ]

    return operations

@router.post("/add/operation", response_model=OperationRead, status_code=201)
def add_operation(name: str = Body(...), required_machine_type: str = Body(...), duration: int = Body(...), material_needed: Optional[str] = Body(None)):
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