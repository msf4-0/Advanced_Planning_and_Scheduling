from typing import List
from datetime import datetime
from repository.db_repository import DBTable
from models import OrderCreate, OrderRead

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
        # Calculate internal priority based on user priority and due date
        # basic formula: (priority + due date) / 2
        priority = ((user_priority / 10) + (1 / (max((due_date - datetime.now()).days, 1))) + 1) / 2

        order = OrderCreate(
            product_id=product_id,
            user_priority=user_priority,
            due_date=due_date,
            quantity=quantity,
            priority=priority
        )
        order_id = self.db.add_order(order)
        if order_id is None:
            raise ValueError("Failed to create order.")
        
        row = self.db.fetch_orders(order_id)
        return OrderRead(
            order_id=row['order_id'],
            product_name=row['product_name'],
            product_id=row['product_id'],
            user_priority=row['priority'],
            quantity=row['quantity'],
            due_date=row['due_date'],
            status=row['status']
        )
    
    def get_order_until(self, date: datetime) -> List[OrderRead]:
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