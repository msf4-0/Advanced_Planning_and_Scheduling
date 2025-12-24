# route_repository.py
from typing import List, Optional
from appsmith.aps_backend.models.api_models import OperationRead, OpStepRead, ProductRouteRead

class RouteRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_steps_for_product(
        self, 
        product_id: int, 
        filters: Optional[dict] = None
    ) -> List[OpStepRead]:
        """
        Fetch only the steps for a product within a given sequence range.
        If start_seq/end_seq are None, fetch all steps.
        
        Args:
            product_id (int): The ID of the product.
            filters (Optional[dict]): A dictionary of filters to apply.
                Supported keys:
                    - 'min_sequence' (int): Minimum sequence number.
                    - 'max_sequence' (int): Maximum sequence number.
                    - 'operation_id' (int): Specific operation ID to filter by.
        """
        filters = filters or {}
        params = [product_id]
        clauses = []

        # Allowed filters
        if 'min_sequence' in filters:
            clauses.append("s.sequence >= %s")
            params.append(filters['min_sequence'])
        if 'max_sequence' in filters:
            clauses.append("s.sequence <= %s")
            params.append(filters['max_sequence'])
        if 'operation_id' in filters:
            clauses.append("o.operation_id = %s")
            params.append(filters['operation_id'])

        where_clause = ""
        if clauses:
            where_clause = "WHERE " + " AND ".join(clauses)

        sql = f"""
        SELECT *
        FROM cypher('production_graph', $$
            MATCH (p:Product {{product_id: %s}})
                  -[:HAS_STEP]->(s:OpStep)
                  -[:DOES]->(o:Operation)
            {where_clause}
            RETURN s.sequence,
                   o.operation_id,
                   o.name,
                   o.duration
            ORDER BY s.sequence
        $$) AS (
            sequence agtype,
            operation_id agtype,
            operation_name agtype,
            duration agtype
        );
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

        return [
            OpStepRead(
                product_id=product_id,
                sequence=int(row[0]),
                operation=OperationRead(
                    operation_id=int(row[1]),
                    name=row[2],
                    duration=int(row[3]),
                ),
            )
            for row in rows
        ]
    
    def get_all_orders(self) -> List[dict]:
        """
        Fetch all orders from the database.
        Returns: list of orders with 'order_id' and 'product_id'
        """
        sql = """
        SELECT * FROM cypher('production_graph', $$
        MATCH (o:Order)
        RETURN o
        $$) AS (o agtype);
        """

        with self.conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()

        return [
            {
                "order_id": row["order_id"],
                "product_name": row["product_name"],
                "priority": row["priority"],
                "due_date": row["due_date"],
                "quantity": row["quantity"]
            }
            for row in rows
        ]
    
    def get_order_operations(self, order_id: int) -> List[dict]:
        """
        Fetch operations for a given order based on its product's route.
        
        Args:
            order_id (int): The ID of the order.
        Returns: list of operations with 'name', 'duration', 'machine_type', 'sequence'
        """

        sql = """
        SELECT op_node
        FROM cypher('production_graph', $$
        MATCH (o:Order {order_id: $order_id})-[:OF_PRODUCT]->(p:Product)-[:HAS_STEP]->(s:OpStep)-[:ASSIGNED_OP]->(op:Operation)
        RETURN op
        ORDER BY s.sequence
        $$) AS (op_node agtype);
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, {'order_id': order_id})
            rows = cur.fetchall()

        return [
            {
                "name": row['op_node']['name'],
                "duration": row['op_node']['duration'],
                "machine_type": row['op_node']['required_machine_type'],
                "sequence": row['op_node']['sequence'],
                "material_needed": row['op_node']['material_needed']
            }
            for row in rows
        ]
    
    def shift_sequences_up(
        self,
        product_id: int,
        starting_sequence: int
    ) -> None:
        """
        Increment the sequence numbers of all OpSteps for a product
        starting from `starting_sequence` to make room for a new step.

        Args:
            product_id (int): The ID of the product.
            starting_sequence (int): The sequence number from which to start shifting.
        """

        sql = """
        SELECT * 
        FROM cypher('production_graph', $$
            MATCH (s:OpStep {product_id: %s})
            WHERE s.sequence >= %s
            SET s.sequence = s.sequence + 1
            RETURN count(s)
        $$) AS (count agtype);
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, (product_id, starting_sequence))
            # No need to fetch results for this operation

    def insert_step(
        self,
        product_id: int,
        sequence: int,
        operation_id: int
    ) -> None:
        """
        Insert a new OpStep node into the graph for the given product
        and link it to the specified operation.

        Args:
            product_id (int): The ID of the product.
            operation_id (int): The ID of the operation to link.
            sequence (int): The sequence number for the new step.
        """

        sql = """
        SELECT * 
        FROM cypher('production_graph', $$
            MATCH (p:Product {product_id: %s}),
                  (o:Operation {operation_id: %s})
            CREATE (s:OpStep {
                product_id: %s,
                sequence: %s
            })
            CREATE (p)-[:HAS_STEP]->(s)
            CREATE (s)-[:DOES]->(o)
            RETURN s
        $$) AS (s agtype);
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, (product_id, operation_id, product_id, sequence))
            # No need to fetch results for this operation

    def rebuild_next_operation_edges(
        self,
        product_id: int
    ) -> None:
        """
        Rebuild the NEXT_OPERATION edges between OpSteps for a product
        to ensure they reflect the correct sequence.

        Args:
            product_id (int): The ID of the product.
        """

        sql = """
        SELECT * 
        FROM cypher('production_graph', $$
            MATCH (s:OpStep {product_id: %s})-[r:NEXT_OPERATION]->()
            DELETE r;

            MATCH (s1:OpStep {product_id: %s})
            MATCH (s2:OpStep {product_id: %s})
            WHERE s2.sequence = s1.sequence + 1
            CREATE (s1)-[:NEXT_OPERATION]->(s2)
            RETURN count(*)
        $$) AS (count agtype);
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, (product_id, product_id, product_id))
            # No need to fetch results for this operation

    def delete_step(
        self,
        product_id: int,
        sequence: int
    ) -> None:
        """
        Delete an OpStep node from the graph for the given product
        based on its sequence number.

        Args:
            product_id (int): The ID of the product.
            sequence (int): The sequence number of the step to delete.
        """

        sql = """
        SELECT * 
        FROM cypher('production_graph', $$
            MATCH (s:OpStep {product_id: %s, sequence: %s})
            DETACH DELETE s
        $$) AS (count agtype);
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, (product_id, sequence))
            # No need to fetch results for this operation

    def shift_sequences_down(
        self,
        product_id: int,
        starting_sequence: int
    ) -> None:
        """
        Decrement the sequence numbers of all OpSteps for a product
        starting from `starting_sequence` to fill the gap after a step deletion.

        Args:
            product_id (int): The ID of the product.
            starting_sequence (int): The sequence number from which to start shifting down.
        """

        sql = """
        SELECT * 
        FROM cypher('production_graph', $$
            MATCH (s:OpStep {product_id: %s})
            WHERE s.sequence > %s
            SET s.sequence = s.sequence - 1
            RETURN count(s) 
        $$) AS (count agtype);
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, (product_id, starting_sequence))
            # No need to fetch results for this operation

    def reassign_sequences(
        self,
        product_id: int,
        mapping: dict[int, int]
    ) -> None:
        """
        Reassign sequence numbers for OpSteps of a product based on a provided mapping.

        Args:
            product_id (int): The ID of the product.
            mapping (dict[int, int]): A dictionary mapping old sequence numbers to new ones.
        """

        for old_seq, new_seq in mapping.items():
            sql = """
            SELECT * 
            FROM cypher('production_graph', $$
                MATCH (s:OpStep {product_id: %s, sequence: %s})
                SET s.sequence = %s
                RETURN s
            $$) AS (s agtype);
            """

            with self.conn.cursor() as cur:
                cur.execute(sql, (product_id, old_seq, new_seq))
                # No need to fetch results for this operation