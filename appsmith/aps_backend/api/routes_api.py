from fastapi import APIRouter, Depends
from models import RouteFilter, ProductRouteRead, OpStepCreate
from service import ProductBlueprintService
from repository import DBTable, GraphEditor  # Make sure to import your connection getter

router = APIRouter()

def get_service():
    conn = DBTable().get_connection()
    graph_editor = GraphEditor(conn)
    try:
        yield ProductBlueprintService(graph_editor)
    finally:
        conn.close()

@router.get("/products/{product_id}/route", response_model=ProductRouteRead)
def get_route(product_id: int, service: ProductBlueprintService = Depends(get_service)):
    """
    Retrieve the full route for a product.

    Location: appsmith/aps_backend/api/routes_api.py
    """
    return service.get_product_sequence(product_id)

@router.post("/products/{product_id}/route/validate")
def validate_route(
    product_id: int,
    filters: RouteFilter,
    service: ProductBlueprintService = Depends(get_service)
):
    """
    Validate that the sequence of OpSteps is continuous for a product.

    Location: appsmith/aps_backend/api/routes_api.py
    """
    service.validate_sequence(
        product_id, 
        filters.model_dump(exclude_none=True)
    )
    return {"status": "ok"}

@router.post("/products/{product_id}/steps")
def add_step(
    product_id: int,
    payload: OpStepCreate,
    service: ProductBlueprintService = Depends(get_service)
):
    """
    Add a new step to the product route.

    Location: appsmith/aps_backend/api/routes_api.py
    """

    service.add_opstep(
        product_id = product_id,
        operation_id = payload.operation_id,
        insert_after = payload.insert_after
    )
    return {"status": "step added"}
