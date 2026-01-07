from fastapi import APIRouter
from models import ProductRouteCreate, ProductRouteRead
from service import ProductBlueprintService
from repository import DBTable, GraphEditor

router = APIRouter()

@router.get(
        "/blueprint/{product_id}/get", 
        response_model=ProductRouteRead,
        tags=["Blueprints"]
        )
def get_route(product_id: int):
    """
    Retrieve the full route for a product.

    Location: appsmith/aps_backend/api/routes_api.py
    """

    db = DBTable()
    graph_editor = GraphEditor(db)
    service = ProductBlueprintService(graph_editor)

    return service.fetch_blueprint(product_id)


@router.post(
        "/blueprint/{product_id}/create",
        tags=["Blueprints"]
        )
def generate_blueprint(
    payload: ProductRouteCreate
):
    """
    Add a new step to the product route.

    Location: appsmith/aps_backend/api/routes_api.py
    """

    db = DBTable()
    graph_editor = GraphEditor(db)
    service = ProductBlueprintService(graph_editor)
    service.create_blueprint(payload)
    
    return {"status": "step added"}
