from repository import DBTable, GraphEditor
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
    
    def regenerate_all_product_nodes(self):
        product_rows = self.db.fetch_product()
        graph_editor = GraphEditor(self.db)

        for row in product_rows:
            product_id = row['product_id']
            product_node = graph_editor.get_node(
                label='Product',
                filters={'product_id': product_id}
            )

            if not product_node:
                graph_editor.create_node(
                    label='Product',
                    properties={'product_id': product_id}
                )