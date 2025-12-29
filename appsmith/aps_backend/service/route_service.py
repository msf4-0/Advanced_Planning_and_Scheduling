from appsmith.aps_backend.repository.opstep_graph_repo import RouteRepository
from models import ProductRouteRead, OpStepRead
from typing import Optional, Dict, List

class RouteService:
    def __init__(self, repo: RouteRepository):
        self.repo = repo

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
        steps = self.repo.get_steps_for_product(product_id, filters=filters)
        
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
        steps = self.repo.get_steps_for_product(product_id, filters=filters)
        
        if not steps:
            raise ValueError("No steps found for the given product / filters")

        seqs = [s.sequence for s in steps]
        expected = list(range(min(seqs), max(seqs) + 1))

        if seqs != expected:
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
        steps = self.repo.get_steps_for_product(product_id)
        if not steps:
            next_seq = 1
        elif insert_after is None:
            next_seq = max(s.sequence for s in steps) + 1
        else:
            next_seq = insert_after + 1

        # shift sequences of existing steps if inserting in the middle
        self.repo.shift_sequences_up(
            product_id=product_id,
            starting_sequence=next_seq
        )

        self.repo.insert_step(
            product_id=product_id,
            operation_id=operation_id,
            sequence=next_seq
        )

        # rebuild NEXT_OPERATION edges
        self.repo.rebuild_next_operation_edges(product_id)

        # validate
        self.validate_route(product_id)

    def delete_step(self, product_id: int, sequence: int) -> None:
        """
        Delete an OpStep from the product's route.

        Args:
            product_id (int): The ID of the product.
            operation_id (int): The ID of the operation to remove.
        """
        steps = self.repo.get_steps_for_product(product_id=product_id)

        if sequence not in [s.sequence for s in steps]:
            raise ValueError("No step found with the given sequence number")
        
        # rebuild NEXT_OPERATION edges
        self.repo.delete_step(product_id, sequence)
        self.repo.shift_sequences_down(product_id, sequence)
        self.repo.rebuild_next_operation_edges(product_id)

        # validate
        self.validate_route(product_id)

    def reorder_steps(self, product_id: int, new_order: List[int]) -> None:
        """
        Reorder the OpSteps for a product based on a new list of operation IDs.

        Args:
            product_id (int): The ID of the product.
            new_order (List[int]): List of operation_ids in the desired order.
        """
        steps = self.repo.get_steps_for_product(product_id=product_id)
        opIdToOldSequence = {
            s.operation.operation_id: s.sequence for s in steps
        }

        if sorted(opIdToOldSequence.keys()) != sorted(new_order):
            raise ValueError("New order must contain the same operation IDs as the current route")

        # Update sequences based on new order
        mapping = {
            opIdToOldSequence[op_id]: new_seq
            for new_seq, op_id in enumerate(new_order, start=1)
        }

        self.repo.reassign_sequences(product_id, mapping)

        # Rebuild NEXT_OPERATION edges
        self.repo.rebuild_next_operation_edges(product_id)

        # Validate
        self.validate_route(product_id)