from fastapi import APIRouter, Body
from typing import List
from datetime import datetime

from repository.db_repository import DBTable
from models import OrderCreate, OrderRead

router = APIRouter()

@router.get("/get/orders", response_model=List[OrderRead])
def get_orders():
    '''
    Fetch the list of orders from the database.
    
    Location: appsmith/aps_backend/api/order_api.py
    '''
    db = DBTable()
    rows = db.fetch_orders()
    orders = [
        OrderRead(
            order_id=row['order_id'],
            product_name=row['product_name'],
            product_id=row['product_id'],
            priority=row['priority'],
            quantity=row['quantity'],
            due_date=row['due_date'],
            status=row['status']
        )
        for row in rows
    ]

    return orders

@router.post("/add/order", response_model=OrderRead, status_code=201)
def add_order(payload: OrderCreate):
    '''
    Add a new order to the system.

    Location: appsmith/aps_backend/api/order_api.py
    '''
    db = DBTable()
    order_id = db.add_order(payload)
    
    if order_id is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Failed to create order.")

    row = db.fetch_orders(order_id)
    order = OrderRead(
        order_id=row['order_id'],
        product_name=row['product_name'],
        product_id=row['product_id'],
        priority=row['priority'],
        quantity=row['quantity'],
        due_date=row['due_date'],
        status=row['status']
    )

    return order