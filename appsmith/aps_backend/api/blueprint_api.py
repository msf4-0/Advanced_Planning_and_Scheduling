from fastapi import APIRouter, Body, HTTPException
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
        "/blueprint/{product_id}/generate",
        tags=["Blueprints"]
        )
def generate_blueprint(
    product_id: int
):
    """
    Add a new step to the product route.

    Location: appsmith/aps_backend/api/routes_api.py
    """

    db = DBTable()
    graph_editor = GraphEditor(db)
    service = ProductBlueprintService(graph_editor)
    service.generate_blueprint_graph(product_id)
    
    return {"status": "step added"}

@router.post(
        "/blueprint/{product_id}/upsert",
        tags=["Blueprints"]
        )
def upsert_blueprint(
    product_id: int,
    payload: ProductRouteCreate = Body(...)
):
    """
    Upsert a step in the product route.

    Location: appsmith/aps_backend/api/routes_api.py
    """

    db = DBTable()
    graph_editor = GraphEditor(db)
    service = ProductBlueprintService(graph_editor)
    product = db.fetch_product(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    service.insert_blueprint_toDB(product_id, payload)
    
    return {"status": "blueprint added"}
