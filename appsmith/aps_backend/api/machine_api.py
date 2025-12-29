from fastapi import APIRouter, Body, HTTPException
from typing import List, Optional

from repository.db_repository import DBTable
from service.machine_service import MachineService

router = APIRouter()

@router.post("/add/machine", response_model=dict, status_code=201)
def add_machine(
    name: str = Body(...),
    machine_type: str = Body(...),
    capacity: int = Body(None)
):
    '''
    Add a new machine to the system.

    Location: appsmith/aps_backend/api/machine_api.py
    '''

    machine_service = MachineService(DBTable())

    try:
        machine_id = machine_service.add_machine(
            name=name,
            machine_type=machine_type,
            capacity=capacity
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "status": "success",
        "machine_id": machine_id,
        "name": name,
        "machine_type": machine_type,
        "capacity": capacity
    }