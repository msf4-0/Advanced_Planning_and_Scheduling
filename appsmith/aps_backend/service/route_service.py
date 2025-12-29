from repository import GraphEditor
from models import ProductRouteRead, OpStepRead, OperationRead
from typing import Optional, Dict, List

class RouteService:
    def __init__(self, graph: GraphEditor):
        self.graph = graph

    # Node / Step Retrieval
    def get_product_sequence(
            self, 
            product_id: int,
            filters: Optional[Dict] = None
        ) -> ProductRouteRead:
        """
        Retrieve the full manufacturing sequence for a product, optionally filtered by sequence range or operation ID.
        
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

        # Fetch OpSteps for the product
        steps = self.graph.get_node('OpStep', node_filters)

        # Apply additional filters
        seq_min = filters.get('min_sequence', 0)
        seq_max = filters.get('max_sequence', float('inf'))
        steps = [
            step for step in steps
            if seq_min <= step['sequence'] <= seq_max
        ]

        # Sort steps by sequence
        steps_sorted = sorted(steps, key=lambda s: s['sequence'])

        # Build OpStepRead objects
        steps_read = []
        for step in steps_sorted:
            op_node = step.get('operation')
            if not op_node:
                op_nodes = self.graph.get_node('Operation', {'operation_id': step['operation_id']})
                op_node = op_nodes[0] if op_nodes else {}

            operation_id = op_node.get('operation_id')
            if operation_id is None:
                raise ValueError(f"Operation node missing 'operation_id' for step {step['id']}")
                
            steps_read.append(
                OpStepRead(
                    product_id=product_id,
                    sequence=step['sequence'],
                    operation=OperationRead(
                        operation_id=operation_id,
                        name=op_node.get('name') or "",
                        duration=op_node.get('duration') or 0,
                        machine_type=op_node.get('required_machine_type') or "",
                        material_id=op_node.get('material_needed')
                    )
                )
            )

        if not steps:
            raise ValueError("No steps found for the given product / sequence range")
        
        return ProductRouteRead(
            product_id=product_id,
            product_name=f"Product {product_id}",  # optionally fetch name from DB if needed
            steps=steps_read
        )


    # Route Validation
    def validate_sequence(
            self, 
            product_id: int, 
            filters: Optional[Dict] = None
        ) -> bool:
        """
        Validate that the manufacturing sequence of OpSteps is continuous for a product.
        Optional `filters` can limit which steps are checked.

        Args:
            product_id (int): The ID of the product.
            filters (Optional[Dict]): A dictionary of filters to apply.
                Supported keys:
                    - 'min_sequence' (int): Minimum sequence number.
                    - 'max_sequence' (int): Maximum sequence number.
                    - 'operation_id' (int): Specific operation ID to filter by.
        """
        route = self.get_product_sequence(product_id, filters)
        sequences = [step.sequence for step in route.steps]
        expected = list(range(min(sequences), max(sequences) + 1))
        
        if sequences != expected:
            raise ValueError("Route sequence is broken")

        return True
    

    # Route Modification
    def add_opstep(
            self,
            product_id: int,
            operation_id: int,
            insert_after: Optional[int] = None
        ) -> None:
        """
        Add a new OpStep to the product's manufacturing process.

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
                        step['id'], 
                        {'sequence': step['sequence'] + 1}
                    )
            
        # Create new OpStep
        new_step_node = self.graph.create_node(
            'OpStep',
            {
                'product_id': product_id,
                'operation_id': operation_id,
                'sequence': next_seq
            }
        )

        new_step_id = new_step_node['id']

        # Link to product
        self.graph.create_edge(from_id=product_id, to_id=new_step_id, edge_type='HAS_STEP')
        # Link to operation
        self.graph.create_edge(from_id=new_step_id, to_id=operation_id, edge_type='DOES')

        # Rebuild NEXT_OPERATION edges
        self.rebuild_next_operation_edges(product_id)

        # validate
        self.validate_sequence(product_id)

    def delete_opstep(self, product_id: int, sequence: int) -> None:
        """
        Delete an OpStep from the product's manufacturing process.

        Args:
            product_id (int): The ID of the product.
            operation_id (int): The ID of the operation to remove.
        """

        try:
            steps = self.graph.get_node('OpStep', {'product_id': product_id})

            # Find the node id to delete
            step_to_delete = next((step for step in steps if step['sequence'] == sequence), None)
            if not step_to_delete:
                raise ValueError("No step found with the given sequence number")
            node_id = step_to_delete['id']
            self.graph.delete_node(node_id)

            # Shift remaining sequences down
            for step in steps:
                if step['sequence'] > sequence:
                    self.graph.update_node('OpStep', step['id'], {'sequence': step['sequence'] - 1})

            # Rebuild NEXT_OPERATION edges
            self.rebuild_next_operation_edges(product_id)

            # Validate
            self.validate_sequence(product_id)

        except Exception as e:
            raise ValueError(f"Failed to delete step: {str(e)}")

    def reorder_opsteps(self, product_id: int, new_order: List[int]) -> None:
        """
        Reorder the OpSteps (manufacturing steps) for a product according to new_order.

        Args:
            product_id (int): The ID of the product.
            new_order (List[int]): List of operation_ids in the desired order.
        """
        steps = self.graph.get_node('OpStep', {'product_id': product_id})
        if sorted([step['operation_id'] for step in steps]) != sorted(new_order):
            raise ValueError("New order must contain the same operation IDs")

        # Update sequences
        op_to_step = {step['operation_id']: step for step in steps}
        for idx, op_id in enumerate(new_order, start=1):
            self.graph.update_node('OpStep', op_to_step[op_id]['id'], {'sequence': idx})

        # Rebuild edges and validate
        self.rebuild_next_operation_edges(product_id)
        self.validate_sequence(product_id)
 
    def rebuild_next_operation_edges(self, product_id: int) -> None:
        """
        Rebuild NEXT_OPERATION edges based on OpStep manufacturing sequences.
        """

        # Remove all existing NEXT_OPERATION edges for this product
        steps = self.graph.get_node('OpStep', {'product_id': product_id})
        step_ids = [step['id'] for step in steps]
        for from_id in step_ids:
            # Find all NEXT_OPERATION edges from this step and delete them individually
            next_op_edges = self.graph.get_edges(from_id=from_id, edge_type='NEXT_OPERATION')
            for edge in next_op_edges:
                self.graph.delete_edge(from_id=from_id, to_id=edge['to_id'], edge_type='NEXT_OPERATION')

        # Sort steps by sequence and create new NEXT_OPERATION edges
        steps_sorted = sorted(steps, key=lambda step: step['sequence'])
        for i in range(len(steps_sorted) - 1):
            from_id = steps_sorted[i]['id']
            to_id = steps_sorted[i + 1]['id']
            self.graph.create_edge(from_id=from_id, to_id=to_id, edge_type='NEXT_OPERATION')

    def rebuild_can_run_on_edges(self) -> None:
        """
        Rebuild CAN_RUN_ON edges for all operations based on required_machine_type.
        """

        # Remove all existing CAN_RUN_ON edges
        edges = self.graph.get_edges(edge_type='CAN_RUN_ON')
        for edge in edges:
            from_id = edge.get('from_id')
            to_id = edge.get('to_id')
            if from_id is not None and to_id is not None:
                self.graph.delete_edge(from_id=from_id, to_id=to_id, edge_type='CAN_RUN_ON')

        # Get all operations and machines
        operations = self.graph.get_node('Operation', {})
        machines = self.graph.get_node('Machine', {})

        # Build a mapping from machine type to machine node id(s)
        machine_type_to_ids = {}
        for machine in machines:
            mtype = machine.get('type')
            if mtype:
                machine_type_to_ids.setdefault(mtype, []).append(machine['id'])

        # For each operation, create CAN_RUN_ON edge(s) to matching machine(s)
        for op in operations:
            required_type = op.get('required_machine_type')
            op_id = op.get('id')
            if required_type and op_id and (required_type in machine_type_to_ids):
                for machine_id in machine_type_to_ids[required_type]:
                    self.graph.create_edge(from_id=op_id, to_id=machine_id, edge_type='CAN_RUN_ON')

    def rebuild_uses_edges(self) -> None:
        """
        Rebuild USES edges for all operations based on material_needed property.
        """
        # Remove all existing USES edges
        edges = self.graph.get_edges(edge_type='USES')
        for edge in edges:
            from_id = edge.get('from_id')
            to_id = edge.get('to_id')
            if from_id is not None and to_id is not None:
                self.graph.delete_edge(from_id=from_id, to_id=to_id, edge_type='USES')

        # Get all operations and materials
        operations = self.graph.get_node('Operation', {})
        materials = self.graph.get_node('Material', {})

        # Build a mapping from material_id to material node id(s)
        material_id_to_ids = {}
        for material in materials:
            mat_id = material.get('material_id')
            if mat_id is not None:
                material_id_to_ids.setdefault(mat_id, []).append(material['id'])

        # For each operation, create USES edge(s) to matching material(s)
        for op in operations:
            material_needed = op.get('material_needed')
            op_id = op.get('id')
            if material_needed and op_id and material_needed in material_id_to_ids:
                for mat_id in material_id_to_ids[material_needed]:
                    self.graph.create_edge(from_id=op_id, to_id=mat_id, edge_type='USES')


    # Fetch steps
    def get_order_operations(self, order_id: int) -> List[dict]:
        """
        Fetch operations for a given order based on its product's manufacturing sequence.

        Args:
            order_id (int): The ID of the order.
        Returns: list of operations with 'name', 'duration', 'machine_type', 'sequence'
        """
        # Get the product_id for the order
        order_nodes = self.graph.get_node('Order', {'order_id': order_id})
        if not order_nodes:
            raise ValueError(f"No order found with order_id={order_id}")
        product_id = order_nodes[0].get('product_id')
        if product_id is None:
            raise ValueError(f"Order {order_id} does not have a product_id")

        # Get OpSteps for the product, sorted by sequence
        opsteps = self.graph.get_node('OpStep', {'product_id': product_id})
        opsteps_sorted = sorted(opsteps, key=lambda s: s['sequence'])

        operations = []
        for step in opsteps_sorted:
            # Get the operation node for this OpStep
            operation = step.get('operation')
            if not operation:
                # Fallback: fetch operation node by operation_id if not embedded
                op_nodes = self.graph.get_node('Operation', {'operation_id': step.get('operation_id')})
                operation = op_nodes[0] if op_nodes else {}
            operations.append({
                "name": operation.get('name'),
                "duration": operation.get('duration'),
                "machine_type": operation.get('required_machine_type'),
                "sequence": step.get('sequence'),
                "material_needed": operation.get('material_needed')
            })
        return operations
    
    def get_ready_opsteps(self) -> List[OpStepRead]:
        """
        Fetch all OpSteps (manufacturing steps) that are ready to be scheduled by ORTools.
        An OpStep is ready if:
        - It has no incoming BLOCKED_BY edges
        - All previous steps (NEXT_OPERATION predecessors) are done
        """
        # Fetch all OpSteps
        steps = self.graph.get_node('OpStep', {})
        id_to_step = {step['id']: step for step in steps}
        ready_steps = []

        for step in steps:
            # Check for incoming BLOCKED_BY edges
            blocked_by_edges = self.graph.get_edges(
                to_id=step['id'],
                edge_type='BLOCKED_BY'
            )
            if blocked_by_edges:
                continue

            # Check all previous steps (NEXT_OPERATION predecessors) are done
            prev_edges = self.graph.get_edges(
                to_id=step['id'],
                edge_type='NEXT_OPERATION'
            )
            all_prev_done = True
            for edge in prev_edges:
                # Get the source node's sequence
                prev_step = id_to_step.get(edge.get('from_id'))    
                if prev_step and prev_step.get('status') != 'done':
                    all_prev_done = False
                    break

            if all_prev_done:
                op_node = step.get('operation')
                if not op_node:
                    op_nodes = self.graph.get_node('Operation', {'operation_id': step['operation_id']})
                    op_node = op_nodes[0] if op_nodes else {}

                operation_id = op_node.get('operation_id')
                if operation_id is None:
                    raise ValueError(f"Operation node missing 'operation_id' for step {step['id']}")
                
                ready_steps.append(
                    OpStepRead(
                        product_id=step['product_id'],
                        sequence=step['sequence'],
                        operation=OperationRead(
                            operation_id=operation_id,
                            name=op_node.get('name') or "",
                            duration=op_node.get('duration') or 0,
                            machine_type=op_node.get('required_machine_type') or "",
                            material_id=op_node.get('material_needed')  # directly use value
                        )
                    )
                )

        return ready_steps



