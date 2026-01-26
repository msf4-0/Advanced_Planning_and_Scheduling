from fastapi import APIRouter, Body, HTTPException, Query
from typing_extensions import List, Optional
from repository import DBTable, GraphEditor
from service import OpStepService

router = APIRouter()

@router.post(
        "/generate-operation-steps/",
        status_code=201,
        tags=["Manufacturing Orders"]
        )
def generate_operation_steps_for_order(
    order_id: int = Query(None)
):
    '''
    Generate operation steps for a specific manufacturing order based on its blueprint.
    Location: appsmith/aps_backend/api/manufacturing_api.py
    '''

    opstep_service = OpStepService(GraphEditor(DBTable()))

    try:
        opstep_service.generate_opstep(order_id=order_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": f"operation steps generated for order {order_id}"}