from fastapi import APIRouter, Body
from typing import List, Optional
from datetime import datetime

from appsmith.aps_backend.repository.db_repository import DBTable

router = APIRouter()

@router.get("/get/products", response_model=List[dict])
def get_products():
    db = DBTable()
    rows = db.fetch_product()
    products = [
        {
            "product_id": row['product_id'],
            "product_name": row['product_name'],
            "description": row['description'],
            "created_at": row['created_at'],
            "updated_at": row['updated_at']
        }
        for row in rows
    ]

    return products

@router.get("/get/product/{product_id}", response_model=dict)
def get_product(product_id: int):
    db = DBTable()
    product = db.fetch_product(product_id=product_id)
    return product

@router.post("/add/product", response_model=dict, status_code=201)
def add_product(products: List[str] = Body(...)):
    db = DBTable()

    products_added = 0

    for product_name in products:
        product_id = db.add_product(product_name=product_name)
        if product_id is not None:
            products_added += 1
    
    return {"products_added": products_added}