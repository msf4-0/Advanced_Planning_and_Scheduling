from fastapi import APIRouter, Body, Query, HTTPException
from typing_extensions import List, Optional
from datetime import datetime

from repository import DBTable
from service import OrderService
from models import OrderRead

router = APIRouter()

@router.get(
        "/get/orders", 
        response_model=List[OrderRead],
        tags=["Orders"]
        )
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

@router.post(
        "/add/order", 
        response_model=OrderRead, 
        status_code=201, 
        tags=["Orders"]
        )
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

    table = DBTable()

    try:
        order_service = OrderService(table)
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
    
@router.post(
        "/generate-order-node/",
        status_code=201,
        tags=["Orders"]
        )
def generate_order_node(
    order_id: Optional[int] = Query(None),
):
    '''
    Generate an order node for the given order ID.
    Location: appsmith/aps_backend/api/order_api.py
    '''

    table = DBTable()
    order_service = OrderService(table)

    try:
        if order_id is None:
            orders = table.fetch_orders()
            for order in orders:
                order_service.generate_order_node(order['order_id'])
        else:
            order_service.generate_order_node(order_id)
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"status": "order node(s) generated"}
    