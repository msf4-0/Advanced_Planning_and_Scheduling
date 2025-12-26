from fastapi import APIRouter, Body
from typing import List
from datetime import datetime

from appsmith.aps_backend.repository.db_repository import DBTable
from appsmith.aps_backend.models import OrderCreate, OrderRead

router = APIRouter()

@router.get("/get/orders", response_model=List[OrderRead])
def get_orders():
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