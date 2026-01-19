import logging
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

@router.put(
        "/add/blueprint/toDB/{product_id}",
        tags=["Blueprints"]
        )
def add_blueprint_toDB(
    product_id: int,
    payload: ProductRouteCreate = Body(...)
):
    """
    Add a blueprint of product route to the DB.

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

@router.post(
    "/update/blueprint/{product_id}",
    tags=["Blueprints"]
)
def update_blueprint(
    product_id: int,
    payload: ProductRouteCreate = Body(...)
):
    """
    Update the product route in the DB.

    Location: appsmith/aps_backend/api/routes_api.py
    """

    db = DBTable()
    graph_editor = GraphEditor(db)
    service = ProductBlueprintService(graph_editor)
    product = db.fetch_product(product_id)
    
    if not product:
        logging.error(f"Product with ID {product_id} not found.")
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        service.reset_blueprint(product_id)
        service.insert_blueprint_toDB(product_id, payload)
        service.generate_blueprint_graph(product_id)
    except Exception as e:
        logging.error(f"Error updating blueprint for product ID {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update blueprint")
    
    return {"status": "blueprint updated"}