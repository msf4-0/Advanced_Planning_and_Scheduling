from repository import DBTable
from typing import Optional

class ProductService:
    def __init__(self):
        self.db = DBTable()

    def fetch_product(self, product_id: Optional[int] = None) -> list[dict]:
        return self.db.fetch_product(product_id=product_id)

    def add_products(self, products: list[str]) -> dict:
        products_added = 0
        products_already_there = 0
        for product_name in products:
            product_id, already_exists = self.db.add_product(product_name=product_name)
            if product_id is not None:
                if already_exists:
                    products_already_there += 1
                else:
                    products_added += 1
        return {
            "products_added": products_added,
            "products_already_there": products_already_there
        }