from typing_extensions import List
from datetime import datetime, timezone
from repository import DBTable, GraphEditor
from models import OrderCreate, OrderRead

import logging

class OrderService:
    def __init__(self, table: DBTable):
        """
        Initialize the OrderService with a database table.
        """
        self.db = table

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
            # scale user_priority to 1-10, 10 is highest priority 
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
    
    def generate_order_node(self, order_id: int) -> dict:
        """
        Generate an order node for the given order ID.

        Args:
            order_id (int): The ID of the order.
        Returns:
            dict: The order node details.
        """
        order = self.db.fetch_orders(order_id=order_id)
        graph = GraphEditor(self.db)

        conn = self.db.get_connection()
        
        if not order:
            raise ValueError(f"Order with ID {order_id} does not exist.")
        
        order_node_in_DB = graph.get_node('Order', {"order_id": order_id}, conn=conn)
        
        if order_node_in_DB:
            logging.info(f"Order node for order_id {order_id} already exists in the graph.")
            order_node = order_node_in_DB[0]
        else:
            order_node = graph.create_node(
                label="Order",
                properties= {
                    "order_id": order[0]['order_id'],
                    "product_id": order[0]['product_id'],
                    "status": order[0]['status']
                    },
                conn=conn
                )
        
        conn.commit()
        conn.close()

        return order_node