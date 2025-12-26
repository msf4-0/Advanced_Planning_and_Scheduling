from fastapi import APIRouter, Body
from typing import List, Optional

from appsmith.aps_backend.repository.db_repository import DBTable
from appsmith.aps_backend.models import OperationRead

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
    db = DBTable()
    material_id = None
    if material_needed:
        material = db.fetch_material(material_name=material_needed)
        if material:
            material_id = material['material_id']
        else:
            material_id = db.add_material(material_needed)
    
    operation_id = db.add_operation(
        name=name, 
        required_machine_type=required_machine_type, 
        duration=duration,
        material_id=material_id
    )
    
    if operation_id is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Failed to create operation.")

    row = db.fetch_operations(operation_id)

    operation = OperationRead(
        operation_id=row[0]['operation_id'],
        name=row[0]['operation_name'],
        duration=row[0]['duration'],
        machine_type=row[0]['machine_type'],
        material_id=row[0].get('material_id')
    )

    return operation