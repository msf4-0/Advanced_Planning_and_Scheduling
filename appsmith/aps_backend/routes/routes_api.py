from fastapi import APIRouter, Depends
from appsmith.aps_backend.models.api_models import RouteFilter, ProductRouteRead, OpStepCreate
from route_service import RouteService
from route_repository import RouteRepository
from appsmith.aps_backend.db.connection import get_connection  # Make sure to import your connection getter

router = APIRouter()

def get_service():
    conn = get_connection()
    try:
        yield RouteService(RouteRepository(conn))
    finally:
        conn.close()

@router.get("/products/{product_id}/route", response_model=ProductRouteRead)
def get_route(product_id: int, service: RouteService = Depends(get_service)):
    return service.get_product_route(product_id)

@router.post("/products/{product_id}/route/validate")
def validate_route(
    product_id: int,
    filters: RouteFilter,
    service: RouteService = Depends(get_service)
):
    
    service.validate_route(
        product_id, 
        filters.model_dump(exclude_none=True)
    )
    return {"status": "ok"}

@router.post("/products/{product_id}/steps")
def add_step(
    product_id: int,
    payload: OpStepCreate,
    service: RouteService = Depends(get_service)
):
    service.add_step_to_route(
        product_id = product_id,
        operation_id = payload.operation_id,
        insert_after = payload.insert_after
    )
    return {"status": "step added"}
