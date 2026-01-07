from typing_extensions import List
from datetime import datetime, timezone
from repository.db_repository import DBTable
from models import OrderCreate, OrderRead

import logging

class OrderService:
    def __init__(self,):
        self.db = DBTable()

    def get_orders(self) -> List[OrderRead]:
        rows = self.db.fetch_orders()
        orders = [
            OrderRead(
                order_id=row['order_id'],
                product_name=row['product_name'],
                product_id=row['product_id'],
                user_priority=row['priority'],
                quantity=row['quantity'],
                due_date=row['due_date'],
                status=row['status']
            )
            for row in rows
        ]
        return orders

    def add_order(self, product_id: int, user_priority: int, due_date: datetime, quantity: int = 1) -> OrderRead:
        
        try:
            # Ensure due_date is timezone-aware (assume UTC if naive)
            if due_date.tzinfo is None:
                due_date = due_date.replace(tzinfo=timezone.utc)
            
            now = datetime.now(timezone.utc)

            # Calculate internal priority based on user priority and due date
            # basic formula: (priority + due date) / 2
            priority = ((user_priority / 10) + (1 / (max((due_date - now).days, 1))) + 1) / 2

            order = OrderCreate(
                product_id=product_id,
                user_priority=user_priority,
                due_date=due_date,
                quantity=quantity,
                priority=priority
            )
            order_id = self.db.add_order(order)
            if order_id is None:
                raise ValueError("db.add_order returned None.")
            
            rows = self.db.fetch_orders(order_id)

            if len(rows) == 0:
                raise ValueError(f"No order found with order_id {order_id} after insertion.")

            return OrderRead(
                order_id=rows[0]['order_id'],
                product_name=rows[0]['product_name'],
                product_id=rows[0]['product_id'],
                user_priority=rows[0]['user_priority'],
                quantity=rows[0]['quantity'],
                due_date=rows[0]['due_date'],
                status=rows[0]['status']
            )
    
        except Exception as e:
            # Log the exception for debugging purposes
            logging.error(f"Error adding order (OrderService.add_order): {e}")
            raise

    def get_order_until(self, date: datetime) -> List[OrderRead]:
        # Ensure date is timezone-aware (assume UTC if naive)
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        
        rows = self.db.fetch_orders()
        filtered_orders = [
            OrderRead(
                order_id=row['order_id'],
                product_name=row['product_name'],
                product_id=row['product_id'],
                user_priority=row['priority'],
                quantity=row['quantity'],
                due_date=row['due_date'],
                status=row['status']
            )
            for row in rows if row['due_date'] <= date
        ]
        return filtered_orders