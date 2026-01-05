from fastapi import APIRouter, Depends
from models import ProductRouteCreate, ProductRouteRead
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

@router.get("/blueprint/{product_id}/get", response_model=ProductRouteRead)
def get_route(product_id: int, service: ProductBlueprintService = Depends(get_service)):
    """
    Retrieve the full route for a product.

    Location: appsmith/aps_backend/api/routes_api.py
    """
    return service.fetch_blueprint(product_id)


@router.post("/blueprint/{product_id}/create")
def generate_blueprint(
    payload: ProductRouteCreate,
    service: ProductBlueprintService = Depends(get_service)
):
    """
    Add a new step to the product route.

    Location: appsmith/aps_backend/api/routes_api.py
    """

    service.create_blueprint(payload)
    return {"status": "step added"}
