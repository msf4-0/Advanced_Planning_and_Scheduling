from fastapi import APIRouter, Depends
from models import RouteFilter, ProductRouteRead, OpStepCreate
from service.route_service import RouteService
from repository.route_repository import RouteRepository
from repository.db_repository import DBTable  # Make sure to import your connection getter

router = APIRouter()

def get_service():
    conn = DBTable().get_connection()
    try:
        yield RouteService(RouteRepository(conn))
    finally:
        conn.close()

@router.get("/products/{product_id}/route", response_model=ProductRouteRead)
def get_route(product_id: int, service: RouteService = Depends(get_service)):
    """
    Retrieve the full route for a product.
    Args:
        product_id (int): The ID of the product.
        service (RouteService): The route service dependency.
    
    Returns:
        ProductRouteRead: The product route data.
    """
    return service.get_product_route(product_id)

@router.post("/products/{product_id}/route/validate")
def validate_route(
    product_id: int,
    filters: RouteFilter,
    service: RouteService = Depends(get_service)
):
    """
    Validate that the sequence of OpSteps is continuous for a product.
    Args:
        product_id (int): The ID of the product.
        filters (RouteFilter): Filters to apply for validation.
        service (RouteService): The route service dependency.

    Returns:
        dict: Status of validation.
    """
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
    """
    Add a new step to the product route.
    
    :param product_id: Description
    :type product_id: int
    :param payload: Description
    :type payload: OpStepCreate
    :param service: Description
    :type service: RouteService
    """

    service.add_step_to_route(
        product_id = product_id,
        operation_id = payload.operation_id,
        insert_after = payload.insert_after
    )
    return {"status": "step added"}
