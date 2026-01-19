import logging
from repository import GraphEditor, DBTable
from typing_extensions import Optional, Any
from enums import ConstraintType, ConstraintStatus, ConstraintSeverity, EdgeType

# filepath: /home/aihunter/Programming/SHRDC_Internship/appsmith/aps_backend/service/constraint_service.py


class ConstraintService:
    """
    Service class to manage constraints for products.
    Communicates between constraint_api and both GraphEditor and DBTable.
    """

    def __init__(self, graph: GraphEditor):
        self.graph = graph
        self.db = graph.get_table()

    def fetch_constraints(self) -> Optional[list[dict]]:
        """
        Retrieve constraints for an order.
        """
        # Fetch all constraint nodes for the order
        nodes = self.graph.get_node('Constraint', {})
        if not nodes:
            return None
        else:
            # Return all constraints for display/edit
            return nodes
        

    def delete_constraint(self, node_id: int) -> None:
        """
        Delete a constraint node by its ID.
        """
        self.graph.delete_node(node_id)


    def add_constraint_graph(self, node_payload: dict) -> None:
        """
        Generate constraints for a node in the graph database.
        """

        conn = self.db.get_connection()
        # self.graph.set_debugging(True)

        # Identify the node type and fetch the corresponding node
        fetch_map = {
            'order_id': self.db.fetch_orders,
            'product_id': self.db.fetch_product,
            'machine_id': self.db.fetch_machines,
            'material_id': self.db.fetch_inventory,
        }

        nodes = []
        for key, fetch_func in fetch_map.items():
            if key in node_payload:
                ids = node_payload.get(key)
                # Always treat as a list for uniformity
                # logging.debug(f"Fetching node for {key}: {id_}")
                if isinstance(ids, list):
                    for id_ in ids:
                        result = fetch_func(id_)
                        if result:
                            nodes.extend(result)
                else:
                    result = fetch_func(ids)
                    if result:
                        nodes.extend(result)

        if not nodes:
            raise ValueError("Invalid payload: missing identifier or no nodes found")

        
        # Create a constraint node linked to the identified node
        
        constraint_type = node_payload.get('type', ConstraintType.CUSTOM_RULE.value)
        constraint_status = node_payload.get('status',  ConstraintStatus.ACTIVE.value)
        constraint_severity = node_payload.get('severity', ConstraintSeverity.INFO.value)
        constraint_description = node_payload.get('description', 'Auto-generated constraint.')


        # # Collect all node IDs by type
        # node_ids_by_type = {'machine_id': [], 'order_id': [], 'product_id': [], 'material_id': []}
        # for node in nodes:
        #     for key in node_ids_by_type.keys():
        #         if key in node:
        #             node_ids_by_type[key].append(node[key])

        # # Remove empty lists
        # affected_nodes = {k: v for k, v in node_ids_by_type.items() if v}

        for node in nodes:
            # Find the node type and id for this node
            node_type = None
            node_id = None
            for key in ['machine_id', 'order_id', 'product_id', 'material_id']:
                if key in node:
                    node_type = key
                    node_id = node[key]
                    break
            affected_nodes = {node_type: node_id} if node_type and node_id is not None else {}

            constraint_props = {
                'type': constraint_type,
                'name': node_payload.get('label'),
                'description': constraint_description,
                'affected_nodes': affected_nodes,
                'status': constraint_status,
                'severity': constraint_severity,
                'metadata': node_payload.get('metadata', {})
            }
            constraint_node = self.graph.create_node('Constraint', constraint_props, conn)

            if not constraint_node:
                logging.error(f"Constraint node creation failed or missing 'id': {constraint_node}")
                raise ValueError("Failed to create constraint node")

            # Use the correct node id for the edge
            node_id = node.get('machine_id') or node.get('order_id') or node.get('product_id') or node.get('material_id')
            self.graph.create_edge(
                from_id=node_id,
                to_id=constraint_node['id'],
                edge_type=EdgeType.BLOCKED_BY.value,
                conn=conn
            )

        conn.commit()
        conn.close()

    def update_constraint_node(self, node_id: int,  node_payload: dict) -> None:
        """
        Update a constraint node in the database.
        """
        nodes = self.graph.get_node('Constraint', {}, node_id=node_id)

        for node in nodes:
            if node['id'] == node_id:
                nodes = [node]
                break

        if not nodes:
            raise ValueError("Constraint node not found")

        # Helper to validate and normalize enum values
        def get_enum_value(enum_cls, value, default):
            try:
                return enum_cls(value).value
            except ValueError:
                return default

        constraint_type = get_enum_value(ConstraintType, node_payload.get('type', ConstraintType.CUSTOM_RULE.value), ConstraintType.CUSTOM_RULE.value)
        constraint_status = get_enum_value(ConstraintStatus, node_payload.get('status', ConstraintStatus.ACTIVE.value), ConstraintStatus.ACTIVE.value)
        constraint_severity = get_enum_value(ConstraintSeverity, node_payload.get('severity', ConstraintSeverity.INFO.value), ConstraintSeverity.INFO.value)

        constraint_props = {
                'type': constraint_type,
                'name': node_payload.get('label'),
                'description': node_payload.get('description', 'Auto-generated constraint.'),
                'affected_nodes': node_payload.get('affected_nodes', {}),
                'status': constraint_status,
                'severity': constraint_severity,
                'metadata': node_payload.get('metadata', {})
            }
        if nodes:
            # Update existing constraint node
            self.graph.update_node(nodes[0]['id'], constraint_props)
        else:
            raise ValueError("Constraint node not found for update")



    