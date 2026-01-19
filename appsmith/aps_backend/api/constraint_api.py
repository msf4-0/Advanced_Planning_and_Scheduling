from fastapi import APIRouter, Body, HTTPException
from service import ConstraintService
from repository import GraphEditor, DBTable
from enums import ConstraintType, ConstraintStatus, ConstraintSeverity

router = APIRouter()

def get_service():
    db = DBTable()
    graph_editor = GraphEditor(db)
    return ConstraintService(graph_editor), db

@router.get(
    "/get/constraint/",
    tags=["Constraints"]
)
def get_constraint():
    service, db = get_service()
    constraint = service.fetch_constraints()

    if not constraint:
        raise HTTPException(status_code=404, detail="No constraints found")
    return constraint
    
@router.get(
    "/get/constraint/enums",
    tags=["Constraints"]
)
def get_constraint_enums():
    return {
        "types": [ct.value for ct in ConstraintType],
        "statuses": [cs.value for cs in ConstraintStatus],
        "severities": [cv.value for cv in ConstraintSeverity]
    }


@router.post(
    "/add/constraint/",
    tags=["Constraints"]
)
def generate_constraint(payload: dict = Body(...)):
    """
    Generate a constraint node in the graph database.
    """
    service, db = get_service()
    try:
        service.add_constraint_graph(payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": "Constraint generated"}


@router.post(
    "/update/constraint/{node_id}",
    tags=["Constraints"]
)
def update_constraint(
    node_id: int,
    payload: dict = Body(...)
):
    """
    Update a constraint node.
    """
    service, db = get_service()
    service.update_constraint_node(node_id, payload)
    return {"message": "Constraint upserted"}


@router.delete(
    "/delete/constraint/node/{node_id}",
    tags=["Constraints"]
)
def delete_constraint(node_id: int):
    service, db = get_service()
    try:
        service.delete_constraint(node_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": "Constraint deleted"}


