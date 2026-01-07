from fastapi import APIRouter, Body
from typing_extensions import List

from service import ProductService

router = APIRouter()

@router.get(
        "/get/products", 
        response_model=List[dict],
        tags=["Products"]
        )
def get_products():
    '''
    Fetch the list of products from the database.
    
    Location: appsmith/aps_backend/api/product_api.py
    '''
    service = ProductService()
    rows = service.fetch_product()
    products = [
        {
            "product_id": row['product_id'],
            "product_name": row['product_name']
        }
        for row in rows
    ]

    return products

@router.get(
        "/get/product/{product_id}", 
        response_model=dict,
        tags=["Products"]
        )
def get_product(product_id: int):
    '''
    Fetch a specific product by its ID.

    Location: appsmith/aps_backend/api/product_api.py
    '''
    service = ProductService()
    product = service.fetch_product(product_id=product_id)
    return product

@router.post(
        "/add/product", 
        response_model=dict, 
        status_code=201,
        tags=["Products"]
        )
def add_product(products: List[str] = Body(...)):
    '''
    Add new products to the database.

    Location: appsmith/aps_backend/api/product_api.py
    '''
    service = ProductService()
    result = service.add_products(products)
    return result