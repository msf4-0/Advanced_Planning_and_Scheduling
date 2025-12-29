from repository import GraphEditor
from models import ProductRouteRead, OpStepRead, OperationRead
from typing import Optional, Dict, List

class RouteService:
    def __init__(self, graph: GraphEditor):
        self.graph = graph

    def get_product_route(
            self, 
            product_id: int,
            filters: Optional[Dict] = None
        ) -> ProductRouteRead:
        """
        Retrieve the full route for a product, optionally filtered by sequence range or operation ID.
        
        Args:
            product_id (int): The ID of the product.
            filters (Optional[Dict]): A dictionary of filters to apply.
                Supported keys:
                    - 'min_sequence' (int): Minimum sequence number.
                    - 'max_sequence' (int): Maximum sequence number.
                    - 'operation_id' (int): Specific operation ID to filter by.
        """
        filters = filters or {}
        node_filters = {'product_id': product_id}
        if 'min_sequence' in filters or 'max_sequence' in filters:
            steps = self.graph.get_node('OpStep', node_filters)
            seq_min = filters.get('min_sequence', 0)
            seq_max = filters.get('max_sequence', float('inf'))
            steps = [
                step for step in steps
                if seq_min <= step['sequence'] <= seq_max
            ]
        else:
            steps = self.graph.get_node('OpStep', node_filters)

        steps_sorted = sorted(steps, key=lambda s: s['sequence'])

        steps = [
            OpStepRead(
                product_id=product_id,
                sequence=step['sequence'],
                operation=OperationRead(
                    operation_id=step['operation']['operation_id'],
                    name=step['operation']['name'],
                    duration=step['operation']['duration'],
                    machine_type=step['operation']['machine_type'],
                    material_id=step['operation']['material_id'].get('material_id')
                )
            )
            for step in steps_sorted
        ]

        if not steps:
            raise ValueError("No steps found for the given product / sequence range")
        
        return ProductRouteRead(
            product_id=product_id,
            product_name=f"Product {product_id}",  # optionally fetch name from DB if needed
            steps=steps
        )

    def validate_route(
            self, 
            product_id: int, 
            filters: Optional[Dict] = None
        ) -> bool:
        """
        Validate that the sequence of OpSteps is continuous for a product.
        Optional `filters` can limit which steps are checked.

        Args:
            product_id (int): The ID of the product.
            filters (Optional[Dict]): A dictionary of filters to apply.
                Supported keys:
                    - 'min_sequence' (int): Minimum sequence number.
                    - 'max_sequence' (int): Maximum sequence number.
                    - 'operation_id' (int): Specific operation ID to filter by.
        """
        route = self.get_product_route(product_id, filters)
        sequences = [step.sequence for step in route.steps]
        expected = list(range(min(sequences), max(sequences) + 1))
        
        if sequences != expected:
            raise ValueError("Route sequence is broken")

        return True
    
    def add_step_to_route(
            self,
            product_id: int,
            operation_id: int,
            insert_after: Optional[int] = None
        ) -> None:
        """
        Add a new OpStep to the product's route.

        Args:
            product_id (int): The ID of the product.
            operation_id (int): The ID of the operation to add as a step.
            insert_after (Optional[int]): The sequence number after which to insert the new step.
                If None, appends to the end of the route.
        """
        # load existing steps to determine next sequence number
        steps = self.graph.get_node('OpStep', {'product_id': product_id})

        if not steps:
            next_seq = 1
        elif insert_after is None:
            next_seq = max(step['sequence'] for step in steps) + 1
        else:
            next_seq = insert_after + 1
            # Shift sequences up
            for step in steps:
                if step['sequence'] >= next_seq:
                    self.graph.update_node(
                        'OpStep', 
                        ('sequence', step['sequence']), 
                        {'sequence': step['sequence'] + 1}
                    )
            
        # Create new OpStep
        new_step = self.graph.create_node(
            'OpStep',
            {
                'product_id': product_id,
                'operation_id': operation_id,
                'sequence': next_seq
            }
        )

        # Link to product
        self.graph.create_edge(
            'Product',
            ('product_id', product_id),
            'OpStep',
            ('sequence', next_seq),
            'HAS_STEP'
        )

        # Link to operation
        self.graph.create_edge(
            'OpStep',
            ('sequence', next_seq),
            'Operation',
            ('operation_id', operation_id),
            'DOES'
        )

        # Rebuild NEXT_OPERATION edges
        self.rebuild_next_operation_edges(product_id)

        # validate
        self.validate_route(product_id)

    def delete_step(self, product_id: int, sequence: int) -> None:
        """
        Delete an OpStep from the product's route.

        Args:
            product_id (int): The ID of the product.
            operation_id (int): The ID of the operation to remove.
        """
        steps = self.graph.get_node('OpStep', {'product_id': product_id})
        if sequence not in [step['sequence'] for step in steps]:
            raise ValueError("No step found with the given sequence number")

        # Delete the step
        self.graph.delete_node('OpStep', ('sequence', sequence))

        # Shift remaining sequences down
        for step in steps:
            if step['sequence'] > sequence:
                self.graph.update_node('OpStep', ('sequence', step['sequence']), {'sequence': step['sequence'] - 1})

        # Rebuild NEXT_OPERATION edges
        self.rebuild_next_operation_edges(product_id)

        # Validate
        self.validate_route(product_id)

    def reorder_steps(self, product_id: int, new_order: List[int]) -> None:
        """
        Reorder the OpSteps for a product based on a new list of operation IDs.

        Args:
            product_id (int): The ID of the product.
            new_order (List[int]): List of operation_ids in the desired order.
        """
        steps = self.graph.get_node('OpStep', {'product_id': product_id})
        if sorted([s['operation']['operation_id'] for s in steps]) != sorted(new_order):
            raise ValueError("New order must contain the same operation IDs")

        # Update sequences
        op_to_step = {s['operation']['operation_id']: s for s in steps}
        for idx, op_id in enumerate(new_order, start=1):
            self.graph.update_node('OpStep', ('sequence', op_to_step[op_id]['sequence']), {'sequence': idx})

        # Rebuild edges and validate
        self.rebuild_next_operation_edges(product_id)
        self.validate_route(product_id)

    def rebuild_next_operation_edges(self, product_id: int) -> None:
        """
        Delete old NEXT_OPERATION edges and recreate based on sequence.
        """
        steps = sorted(self.graph.get_node('OpStep', {'product_id': product_id}), key=lambda s: s['sequence'])
        # Delete existing edges
        for step in steps:
            self.graph.delete_node('OpStep', ('sequence', step['sequence']))
        # Recreate edges
        for i in range(len(steps) - 1):
            self.graph.create_edge(
                'OpStep',
                ('sequence', steps[i]['sequence']),
                'OpStep',
                ('sequence', steps[i + 1]['sequence']),
                'NEXT_OPERATION'
            )