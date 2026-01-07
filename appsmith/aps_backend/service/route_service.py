import logging
from repository import GraphEditor, DBTable
from models import OpStepRead, OperationRead, ProductRouteCreate
from typing_extensions import List
from enums import EdgeType

class OpStepService:
    """
    Service class to manage OpSteps (manufacturing steps) for products.
    """
    def __init__(self, graph: GraphEditor):
        self.graph = graph
        self.blueprint_service = ProductBlueprintService(graph)

    def generate_opstep(
            self,
            product_id: int,
            order_id: int
        ):
        """
        Add a new OpStep to the product's manufacturing process.
        
        :param product_id: ID of the product
        :type product_id: int
        :param operation_id: ID of the operation to add as a step
        :type operation_id: int
        :param order_id: ID of the order associated with this step
        :type order_id: int
        :param insert_after: Sequence number after which to insert the new step.
                             If None, appends to the end of the route.
        :type insert_after: Optional[int]
        """
        
        product_node = self.graph.get_node('Product', {'product_id': product_id})
        if not product_node:
            raise ValueError(f"Product with id {product_id} does not exist")
        
        blueprint = self.blueprint_service.fetch_blueprint(product_id)

        opstep_nodes = {} # key: sequence, value: node
        
        for step in blueprint['manufacturing_line']:
            operation_id = step['operation_id']
            sequence = step['sequence']

            # Create OpStep node
            opstep_node = self.graph.create_node(
                'OpStep',
                {
                    'operation_id': operation_id,
                    'sequence': sequence,
                    'status': 'pending',
                    'order_id': order_id
                }
            )

            opstep_nodes[sequence] = opstep_node

            # link OpStep to Order
            self.graph.create_edge(
                from_id = order_id, 
                to_id = opstep_node['id'], 
                edge_type=EdgeType.USES_STEP.value
                )
            
        # copy BLOCKED_BY edges from Blueprint to OpStep
        for step in blueprint['manufacturing_line']:
            current = opstep_nodes[step['sequence']]
            depends_on = step.get('depends_on', [])

            for dep_sequence in depends_on:
                dep_node = opstep_nodes[dep_sequence]

                self.graph.create_edge(
                    from_id = current['id'], 
                    to_id = dep_node['id'], 
                    edge_type=EdgeType.BLOCKED_BY.value
                )

        sorted_steps = sorted(opstep_nodes.items())
        for index in range(len(sorted_steps) - 1):
            _, current_step = sorted_steps[index]
            _, next_step = sorted_steps[index + 1]

            self.graph.create_edge(
                from_id = current_step['id'], 
                to_id = next_step['id'], 
                edge_type=EdgeType.NEXT_OPERATION.value
            )

     # Fetch steps
    def fetch_order_plan(self, order_id: int) -> dict:
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

        # Get OpSteps for the product, sorted by sequence
        opsteps = self.graph.get_node('OpStep', {'order_id': order_id})
        id_to_step = {step['id']: step for step in opsteps}

        steps = []
        for step in id_to_step.values():
            # Get blocked_by edges to determine dependencies
            blocked_edges = self.graph.get_edges(
                from_id = step['id'],
                edge_type=EdgeType.BLOCKED_BY.value
            )

            depends_on = []
            for edge in blocked_edges:
                depends_on_step = id_to_step.get(edge['to_id'])
                if depends_on_step:
                    depends_on.append(depends_on_step['sequence'])
            
            steps.append({
                'operation_id': step['operation_id'],
                'sequence': step['sequence'],
                'depends_on': depends_on
            })

        return {'order_id': order_id, 'manufacturing_line': steps}
    

    def get_ready_opsteps(self) -> List[OpStepRead]:
        """
        Fetch all OpSteps (manufacturing steps) that are ready to be scheduled by ORTools.
        An OpStep is ready if:
        - It has no outgoing BLOCKED_BY edges
        - All previous steps (NEXT_OPERATION predecessors) are done

        Returns:
            List[OpStepRead]: List of ready OpSteps with their associated Operation details.
        """
        # Fetch all OpSteps
        steps = self.graph.get_node('OpStep', {})
        id_to_step = {step['id']: step for step in steps}
        ready_steps = []

        for step in id_to_step.values():
            # Check for outgoing BLOCKED_BY edges
            blocked_by_edges = self.graph.get_edges(
                from_id=step['id'],
                edge_type=EdgeType.BLOCKED_BY.value
            )

            all_deps_done = True
            for edge in blocked_by_edges:
                dep_step = id_to_step.get(edge['to_id'])
                if dep_step and dep_step.get('status') != 'done':
                    all_deps_done = False
                    break
            
            if not all_deps_done:
                continue # Step is blocked, skip

            op_node = step.get('operation')
            if not op_node:
                op_nodes = self.graph.get_node('Operation', {'operation_id': step['operation_id']})
                op_node = op_nodes[0] if op_nodes else {}
                
            operation_id = op_node.get('operation_id')
            if operation_id is None:
                raise ValueError(f"Operation node missing 'operation_id' for step {step['id']}")
            
            ready_steps.append(
                OpStepRead(
                    order_id=step['order_id'],
                    sequence=step['sequence'],
                    operation=OperationRead(
                        operation_id=operation_id,
                        name=op_node.get('name') or "",
                        duration=op_node.get('duration') or -1,
                        machine_type=op_node.get('required_machine_type') or -1,
                        material_id=op_node.get('material_needed')  # directly use value
                    )
                )
            )

        return ready_steps

     
class ProductBlueprintService:
    def __init__(self, graph: GraphEditor):
        self.graph = graph

    def generate_blueprint_graph(self, product_id: int) -> None:
        """
        Create a manufacturing route for a product by adding OpSteps in sequence.
        
        Args:
            product_id (int): The ID of the product.
            steps (List[Dict]): List of steps, each with 'operation_id' and 'order_id'.
        """

        try:

            dbTemp = DBTable()
            product = dbTemp.fetch_product(product_id)

            if not product:
                raise ValueError(f"Product with id {product_id} does not exist")
                
            payload = dbTemp.fetch_product_blueprint(product_id)

            for step in payload:
                operation_id = step['operation_id']
                sequence = step['sequence']
                depends_on = step.get('depends_on', [])
                
                operation_node = self.graph.get_node('Operation', {'operation_id': operation_id})

                if not operation_node:
                    raise ValueError(f"Operation with id {operation_id} does not exist")
                
                routestep = self.graph.create_node(
                    'RouteStep',
                    {
                        'product_id': product_id,
                        'operation_id': operation_id,
                        'sequence': sequence,
                    }
                )

                # Link to Product
                self.graph.create_edge(
                    from_id = product_id, 
                    to_id = routestep['id'], 
                    edge_type=EdgeType.HAS_ROUTE_STEP.value
                )

                # Link to Operation
                self.graph.create_edge(
                    from_id = routestep['id'],
                    to_id = int(operation_id),
                    edge_type=EdgeType.DOES.value
                )

                # Link dependencies (BLOCKED_BY edges)
                for dep_sequence in depends_on:
                    dep_node = self.graph.get_node('RouteStep', {
                        'product_id': product_id,
                        'sequence': dep_sequence
                    })

                    if dep_node:
                        self.graph.create_edge(
                            from_id = routestep['id'], 
                            to_id = dep_node[0]['id'], 
                            edge_type=EdgeType.BLOCKED_BY.value
                        )

        except Exception as e:
            logging.error("ProductBlueprintService.create_blueprint: %s", e)
            raise e

    def fetch_blueprint(self, product_id: int):
        """
        Fetch the manufacturing route for a product.
        
        Args:
            product_id (int): The ID of the product.
        """

        blueprint_node = self.graph.get_node('Product', {'product_id': product_id})

        if not blueprint_node:
            raise ValueError(f"Product with id {product_id} does not exist")
        
        route_steps = self.graph.get_node('RouteStep', {'product_id': product_id})
        id_to_step = {step['id']: step for step in route_steps}

        steps = []

        for step in route_steps:
            blocked_edges = self.graph.get_edges(
                from_id = step['id'],
                edge_type=EdgeType.BLOCKED_BY.value
            )

            depends_on = []
            for edge in blocked_edges:
                depends_on_step = id_to_step.get(edge['to_id'])
                if depends_on_step:
                    depends_on.append(depends_on_step['sequence'])

            steps.append({
                'operation_id': step['operation_id'],
                'sequence': step['sequence'],
                'depends_on': depends_on
            })

        return {
            'product_id': product_id,
            'manufacturing_line': steps
        }

    def reset_blueprint(self, product_id: int) -> None:
        """
        Delete all RouteSteps associated with a product's manufacturing route.
        
        Args:
            product_id (int): The ID of the product.
        """

        route_steps = self.graph.get_node('RouteStep', {'product_id': product_id})

        for step in route_steps:
            self.graph.delete_node(step['id'])

    def insert_blueprint_toDB(self, product_id: int, payload: ProductRouteCreate) -> None:
        """
        Insert the manufacturing route of a product into the database.

        Args:
            product_id (int): The ID of the product.
        """

        dbTemp = DBTable()

        try:
            for step in payload.manufacturing_line:
                dbTemp.add_product_blueprint_step(
                    product_id=product_id,
                    operation_id=step['operation_id'],
                    sequence=step['sequence'],
                    depends_on=step['depends_on']
                )
        except Exception as e:
            logging.error("[ProductBlueprintService.insert_blueprint_toDB] Err: %s", e)
            raise e