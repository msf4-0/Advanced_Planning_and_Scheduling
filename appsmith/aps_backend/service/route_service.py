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
        self.db = graph.get_table()
        self.blueprint_service = ProductBlueprintService(graph)

    def generate_opstep(
            self,
            order_id: int
        ):
        """
        Add a new OpStep to the product's manufacturing process.
        
        :param product_id: ID of the product
        :type product_id: int
        :param order_id: ID of the order associated with this step
        :type order_id: int
        """
        conn = self.db.get_connection()
        
        order_node = self.graph.get_node('Order', {'order_id': order_id}, conn=conn)
        if not order_node:
            raise ValueError(f"Order with id {order_id} does not exist")
        
        product_id = order_node[0]['product_id']

        product_node = self.graph.get_node('Product', {'product_id': product_id}, conn=conn) # If there's a node then there's a blueprint
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
                },
                conn=conn
            )

            opstep_nodes[sequence] = opstep_node

            # link OpStep to Order
            self.graph.create_edge(
                from_id = order_node[0]['id'], 
                to_id = opstep_node['id'], 
                edge_type=EdgeType.USES_STEP.value,
                conn=conn
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
                    edge_type=EdgeType.BLOCKED_BY.value,
                    conn=conn
                )

        # create NEXT_OPERATION edges
        sorted_steps = sorted(opstep_nodes.items())
        for index in range(len(sorted_steps) - 1):
            _, current_step = sorted_steps[index]
            _, next_step = sorted_steps[index + 1]

            self.graph.create_edge(
                from_id = current_step['id'], 
                to_id = next_step['id'], 
                edge_type=EdgeType.NEXT_OPERATION.value,
                conn=conn
            )

        conn.commit()
        conn.close()

    # Fetch steps
    def fetch_order_plan(self, order_id: int) -> dict:
        """
        Fetch operations for a given order based on its product's manufacturing sequence.

        Args:
            order_id (int): The ID of the order.
        Returns: list of operations with 'name', 'duration', 'machine_type', 'sequence'
        """
        conn = self.db.get_connection()
        
        # Get the product_id for the order
        order_nodes = self.graph.get_node('Order', {'order_id': order_id}, conn=conn)
        if not order_nodes:
            raise ValueError(f"No order found with order_id={order_id}")

        # Get OpSteps for the product, sorted by sequence
        opsteps = self.graph.get_node('OpStep', {'order_id': order_id}, conn=conn)
        id_to_step = {step['id']: step for step in opsteps}

        steps = []
        for step in id_to_step.values():
            # Get blocked_by edges to determine dependencies
            blocked_edges = self.graph.get_edges(
                from_id = step['id'],
                edge_type=EdgeType.BLOCKED_BY.value,
                conn=conn
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

        conn.commit()
        conn.close()
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
        
        conn = self.db.get_connection()

        # Fetch all OpSteps
        steps = self.graph.get_node('OpStep', {}, conn=conn)
        id_to_step = {step['id']: step for step in steps}
        ready_steps = []

        for step in id_to_step.values():
            # Check for outgoing BLOCKED_BY edges
            blocked_by_edges = self.graph.get_edges(
                from_id=step['id'],
                edge_type=EdgeType.BLOCKED_BY.value,
                conn=conn
            )

            # Check if all dependencies are done
            all_deps_done = True
            for edge in blocked_by_edges:
                dep_step = id_to_step.get(edge['end_id'])
                if dep_step and dep_step.get('status') != 'done':
                    all_deps_done = False
                    break
            
            # If there are still BLOCKED_BY edges or dependencies not done, skip this step
            if not all_deps_done:
                continue # Step is blocked, skip

            # Fetch associated Operation details
            op_node = step['operation_id']
            op_data = self.db.fetch_operations(op_node)
            
            ready_steps.append(
                OpStepRead(
                    op_step_id=step['id'],
                    order_id=step['order_id'],
                    sequence_num=step['sequence'],
                    operation=OperationRead(
                        operation_id=op_node,
                        name=op_data[0]['name'] or "",
                        duration=op_data[0]['duration'] or -1,
                        machine_type=op_data[0]['type_id'] or -1,
                        material_id=op_data[0]['material_id']  # directly use value
                    )
                )
            )

        conn.commit()
        conn.close()
        return ready_steps

     
class ProductBlueprintService:
    def __init__(self, graph: GraphEditor):
        self.graph = graph
        self.db = graph.get_table()

    def generate_blueprint_graph(self, product_id: int) -> None:
        """
        Create a manufacturing route for a product by adding OpSteps in sequence.
        
        Args:
            product_id (int): The ID of the product.
            steps (List[Dict]): List of steps, each with 'operation_id' and 'order_id'.
        """

        try:
            conn = self.db.get_connection()
            product = self.db.fetch_product(product_id)

            if not product:
                raise ValueError(f"Product with id {product_id} does not exist")
                
            payload = self.db.fetch_product_blueprint(product_id)

            for step in payload:

                # logging.info(f"Processing step: {step}")

                operation_id = step['operation_id']
                sequence = step['sequence']
                depends_on = step.get('depends_on', [])

                # logging.info(f"Creating RouteStep for operation_id={operation_id},\n sequence={sequence},\n depends_on={depends_on}")
                
                operation_node = self.graph.get_node('Operation', {'operation_id': operation_id}, conn=conn)
                product_node = self.graph.get_node('Product', {'product_id': product_id}, conn=conn)

                if not operation_node:
                    raise ValueError(f"Operation with id {operation_id} does not exist")
                
                if not product_node:
                    raise ValueError(f"Product with id {product_id} does not exist")
                
                routestep_node = self.graph.get_node(
                    'RouteStep', 
                    {
                        'product_id': product_id,
                        'operation_id': operation_id,
                        'sequence': sequence
                    },
                    conn=conn
                )

                if routestep_node:
                    routestep = routestep_node[0]
                else:
                    routestep = self.graph.create_node(
                        'RouteStep',
                        {
                            'product_id': product_id,
                            'operation_id': operation_id,
                            'sequence': sequence,
                        },
                        conn=conn
                    )

                product_node_id = product_node[0]['id']

                has_route_step_edges = self.graph.get_edges(
                    from_id = product_node_id,
                    to_id = routestep['id'],
                    edge_type=EdgeType.HAS_ROUTE_STEP.value,
                    conn=conn
                )

                does_edges = self.graph.get_edges(
                    from_id = routestep['id'],
                    to_id = operation_node[0]['id'],
                    edge_type=EdgeType.DOES.value,
                    conn=conn
                )

                if not has_route_step_edges:
                    # Link to Product
                    self.graph.create_edge(
                        from_id = product_node_id, 
                        to_id = routestep['id'], 
                        edge_type=EdgeType.HAS_ROUTE_STEP.value,
                        conn=conn
                    )

                if not does_edges:
                    # Link to Operation
                    self.graph.create_edge(
                        from_id = routestep['id'],
                        to_id = operation_node[0]['id'],
                        edge_type=EdgeType.DOES.value,
                        conn=conn
                    )

                # Link dependencies (BLOCKED_BY edges)
                # Link to sequence, not operation_id
                for dep_sequence in depends_on:
                    logging.info(f"Linking dependency for sequence {sequence} on dep_sequence {dep_sequence}")
                    dep_node = self.graph.get_node(
                        'RouteStep', 
                        {
                            'product_id': product_id,
                            'sequence': dep_sequence
                        }, 
                        conn=conn
                    )
                    logging.info(f"Found dep_node: {dep_node}")
                    if dep_node:
                        existing_edges = self.graph.get_edges(
                                            from_id = routestep['id'],
                                            to_id = dep_node[0]['id'],
                                            edge_type=EdgeType.BLOCKED_BY.value,
                                            conn=conn
                                        )
                        
                        if not existing_edges:
                            self.graph.create_edge(
                                from_id = routestep['id'], 
                                to_id = dep_node[0]['id'], 
                                edge_type=EdgeType.BLOCKED_BY.value,
                                conn=conn
                            )

            conn.commit()
            conn.close()

        except Exception as e:
            logging.error("ProductBlueprintService.create_blueprint: %s", e)
            raise e

    def fetch_blueprint(self, product_id: int):
        """
        Fetch the manufacturing route for a product.
        
        Args:
            product_id (int): The ID of the product.
        """

        conn = self.db.get_connection()

        blueprint_node = self.graph.get_node('Product', {'product_id': product_id}, conn=conn)

        if not blueprint_node:
            raise ValueError(f"Product with id {product_id} does not exist")
        
        route_steps = self.graph.get_node('RouteStep', {'product_id': product_id}, conn=conn)
        id_to_step = {int(step['id']): step for step in route_steps}

        steps = []

        for step in route_steps:
            blocked_edges = self.graph.get_edges(
                from_id = step['id'],
                edge_type=EdgeType.BLOCKED_BY.value,
                conn=conn
            )
            logging.info(f"Blocked edges for step {step['id']}: {blocked_edges}")

            depends_on = []
            for edge in blocked_edges:
                dep_id = int(edge['end_id'])
                logging.info(f"Checking dep_id: {dep_id}, id_to_step keys: {list(id_to_step.keys())}")
                depends_on_step = id_to_step.get(dep_id)
                if depends_on_step:
                    depends_on.append(depends_on_step['sequence'])
                else:
                    logging.warning(f"dep_id {dep_id} not found in id_to_step mapping.")

            steps.append({
                'operation_id': step['operation_id'],
                'sequence': step['sequence'],
                'depends_on': depends_on
            })

        conn.commit()
        conn.close()
        logging.info(f"Fetched blueprint for product_id {product_id}: {steps}")
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

        conn = self.db.get_connection()

        route_steps = self.graph.get_node('RouteStep', {'product_id': product_id}, conn=conn)

        logging.info(f"RouteSteps to delete for product_id {product_id}: {route_steps}")

        for step in route_steps:
            logging.info(f"Deleting RouteStep with id {step['id']}")
            self.graph.delete_node(step['id'], conn=conn)

        conn.commit()
        conn.close()

    def insert_blueprint_toDB(self, product_id: int, payload: ProductRouteCreate) -> None:
        """
        Insert the manufacturing route of a product into the database.

        Args:
            product_id (int): The ID of the product.
        """

        try:
            for step in payload.manufacturing_line:
                self.db.add_product_blueprint_step(
                    product_id=product_id,
                    operation_id=step['operation_id'],
                    sequence=step['sequence'],
                    depends_on=step['depends_on']
                )
        except Exception as e:
            logging.error("[ProductBlueprintService.insert_blueprint_toDB] Err: %s", e)
            raise e