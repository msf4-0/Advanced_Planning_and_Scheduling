from fastapi import APIRouter, Body
from typing_extensions import List
from datetime import datetime

from repository import DBTable
from service import OrderService
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
            user_priority=row['user_priority'],
            quantity=row['quantity'],
            due_date=row['due_date'],
            status=row['status']
        )
        for row in rows
    ]

    return orders

@router.post("/add/order", response_model=OrderRead, status_code=201)
def add_order(
    product_id: int = Body(...), 
    user_priority: int = Body(...), 
    due_date: datetime = Body(...), 
    quantity: int = Body(1)
    ) -> OrderRead:
    '''
    Add a new order to the system.

    Location: appsmith/aps_backend/api/order_api.py
    '''

    try:
        order_service = OrderService()
        order = order_service.add_order(
            product_id=product_id,
            user_priority=user_priority,
            due_date=due_date,
            quantity=quantity
        )

        return order

    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Error creating order: {e}")