from fastapi import APIRouter, Body, HTTPException
from models import ProductRouteCreate, ProductBlueprintRead
from service import ProductBlueprintService
from repository import DBTable, GraphEditor

router = APIRouter()

@router.get(
    "/get/blueprint/{product_id}", 
    response_model=ProductBlueprintRead,
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

    blueprint = service.fetch_blueprint(product_id)

    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")

    return blueprint


@router.post(
        "/generate/blueprint/{product_id}",
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
        "/upsert/blueprint/{product_id}",
        tags=["Blueprints"]
        )
def upsert_blueprint(
    product_id: int,
    payload: ProductRouteCreate = Body(...)
):
    """
    Upsert a step in the product route DB.

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

@router.delete(
        "/delete/blueprint/{product_id}",
        tags=["Blueprints"]
        )
def delete_blueprint(
    product_id: int
):
    """
    Delete the product route from the DB.

    Location: appsmith/aps_backend/api/routes_api.py
    """

    db = DBTable()
    graph_editor = GraphEditor(db)
    service = ProductBlueprintService(graph_editor)
    product = db.fetch_product(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    service.reset_blueprint(product_id)
    
    return {"status": "blueprint deleted"}