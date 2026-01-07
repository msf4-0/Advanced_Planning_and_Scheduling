from fastapi import APIRouter, Body, HTTPException, Query
from repository import DBTable
from service import MachineService

router = APIRouter()

@router.get(
        "/get/machines",
        response_model=list[dict],
        tags=["Machines"]
        )
def get_machines(
    machine_id: int = Query(None),
    machine_name: str = Query(None)
):
    '''
    Fetch the list of machines from the database.

    Location: appsmith/aps_backend/api/machine_api.py
    '''

    machine_service = MachineService(DBTable())
    machines = machine_service.fetch_machine(
        machine_id=machine_id,
        machine_name=machine_name
    )

    return machines

@router.post(
        "/add/machine", 
        response_model=dict, 
        status_code=201,
        tags=["Machines"]
        )
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

@router.post(
        "/generate/machine_node/{machine_id}",
        status_code=201,
        tags=["Machines"]
        )
def generate_machine_node(machine_id: int):
    '''
    Generate a machine node for the given machine ID.

    Location: appsmith/aps_backend/api/machine_api.py
    '''

    machine_service = MachineService(DBTable())

    try:
        machine_service.generate_machine_node(machine_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {"status": "machine node generated"}