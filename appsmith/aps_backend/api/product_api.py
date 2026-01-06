from fastapi import APIRouter, Body
from typing_extensions import List

from repository.db_repository import DBTable

router = APIRouter()

@router.get("/get/products", response_model=List[dict])
def get_products():
    '''
    Fetch the list of products from the database.
    
    Location: appsmith/aps_backend/api/product_api.py
    '''
    db = DBTable()
    rows = db.fetch_product()
    products = [
        {
            "product_id": row['product_id'],
            "product_name": row['product_name']
        }
        for row in rows
    ]

    return products

@router.get("/get/product/{product_id}", response_model=dict)
def get_product(product_id: int):
    '''
    Fetch a specific product by its ID.

    Location: appsmith/aps_backend/api/product_api.py
    '''
    db = DBTable()
    product = db.fetch_product(product_id=product_id)
    return product

@router.post("/add/product", response_model=dict, status_code=201)
def add_product(products: List[str] = Body(...)):
    '''
    Add new products to the database.

    Location: appsmith/aps_backend/api/product_api.py
    '''
    db = DBTable()

    products_added = 0

    for product_name in products:
        product_id = db.add_product(product_name=product_name)
        if product_id is not None:
            products_added += 1
    
    return {"products_added": products_added}