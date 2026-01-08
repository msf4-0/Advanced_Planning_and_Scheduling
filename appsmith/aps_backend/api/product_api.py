from fastapi import APIRouter, Body, Query
from typing_extensions import List

from service import ProductService

router = APIRouter()

@router.get(
        "/get/products", 
        response_model=List[dict],
        tags=["Products"]
        )
def get_products(product_id: int = Query(None)):
    '''
    Fetch the list of products from the database.
    
    Location: appsmith/aps_backend/api/product_api.py
    '''
    service = ProductService()
    product = service.fetch_product(product_id=product_id)
    products = [
        {
            "product_id": row['product_id'],
            "product_name": row['product_name']
        }
        for row in product
    ]
    return products

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

@router.post(
        "/regenerate-product-nodes",
        tags=["Products"]
        )
def regenerate_product_nodes():
    service = ProductService()
    service.regenerate_all_product_nodes()
    return {"status": "all product nodes regenerated"}
