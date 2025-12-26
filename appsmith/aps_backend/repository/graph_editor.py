from typing import Optional


class GraphEditor:
    def __init__(self, conn):
        self.conn = conn

    # Node Operations
    def create_node(self, label: str, properties: dict) -> dict:
        """
        Create a node with the given label and properties.

        Args:
            label (str): The label of the node.
            properties (dict): A dictionary of properties for the node.

        Returns:
            dict: The created node's properties.
        """

        if not properties:
            props_str = ''
            params = ()
        else:
            for key in properties.keys():
                if not isinstance(key, str):
                    raise ValueError("All property keys must be strings.")
        
        props_str = ', '.join(f"{k}: %s" for k in properties.keys())
        sql = f"""
        SELECT * 
        FROM cypher('production_graph', $$
            CREATE (n:{label} {{{props_str}}})
            RETURN n
        $$) AS (node agtype);
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, tuple(properties.values()))
            result = cur.fetchone()
            return result[0]['node']  # Return the node properties
        

    def get_node(self,label: str, filters: dict) -> list[dict]:
        """
        Retrieve nodes with the given label and optional filters.

        Args:
            label (str): The label of the node.
            filters (dict): A dictionary of properties to filter by.

        Returns:
            list[dict]: A list of nodes matching the criteria.
        """
        if filters:
            for key in filters.keys():
                if not isinstance(key, str):
                    raise ValueError("All filter keys must be strings.")
                
            filter_str = ' AND '.join(f"n.{k} = %s" for k in filters.keys())
            sql = f"""
            SELECT * 
            FROM cypher('production_graph', $$
                MATCH (n:{label})
                WHERE {filter_str}
                RETURN n
            $$) AS (node agtype);
            """
            params = tuple(filters.values())
        else:
            sql = f"""
            SELECT * 
            FROM cypher('production_graph', $$
                MATCH (n:{label})
                RETURN n
            $$) AS (node agtype);
            """
            params = ()

        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            return [row[0]['node'] for row in rows]  # Return list of node properties
        

    def update_node(self, label: str, node_id: tuple[str, int], properties: dict) -> dict:
        """
        Update a node's properties.

        Args:
            label (str): The label of the node.
            node_id (tuple[str, int]): A tuple of (property_key, property_value) to identify the node.
            properties (dict): A dictionary of properties to update.

        Returns:
            dict: The updated node's properties.
        """

        id_key, id_value = node_id
        if not id_key or not isinstance(id_key, str):
            raise ValueError("The property key for node identification must be a non-empty string.")
        if not properties:
            raise ValueError("Properties to update cannot be empty.")
        for key in properties.keys():
            if not isinstance(key, str):
                raise ValueError("All property keys must be strings.")

        set_str = ', '.join(f"n.{k} = %s" for k in properties.keys())
        sql = f"""
        SELECT * 
        FROM cypher('production_graph', $$
            MATCH (n:{label} {{{id_key}: %s}})
            SET {set_str}
            RETURN n
        $$) AS (node agtype);
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, (node_id, *properties.values()))
            result = cur.fetchone()
            return result[0]['node']  # Return the updated node properties


    def delete_node(self, label: str, node_id: tuple[str, int]) -> None:
        """
        Delete a node with the given label and property.

        Args:
            label (str): The label of the node.
            property_key (str): The property key to identify the node.
            property_value: The property value to identify the node.
        """
        id_key, id_value = node_id
        if not id_key.isidentifier():
            raise ValueError("The property key must be a valid identifier.")
        
        sql = f"""
        SELECT * 
        FROM cypher('production_graph', $$
            MATCH (n:{label} {{{id_key}: %s}})
            DETACH DELETE n
        $$) AS (count agtype);
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, (id_value,))
            # No need to fetch results for this operation

    
    # Edge Operations
    def create_edge(self, from_label: str, from_id: tuple[str, int], to_label: str, to_id: tuple[str, int], edge_type: str) -> dict:
        """
        Create an edge of given type between two nodes.
        Args:
            from_label (str): Label of the starting node.
            from_id (tuple[str, int]): (property_key, property_value) of the starting node.
            to_label (str): Label of the ending node.
            to_id (tuple[str, int]): (property_key, property_value) of the ending node.
            edge_type (str): Type of the edge.

        Returns:
            dict: The created edge's properties.
        """
        
        from_key, from_value = from_id
        to_key, to_value = to_id

        for v in [from_key, to_key, edge_type, from_label, to_label]:
            if not v.isidentifier():
                raise ValueError(f"Property keys and edge type must be valid identifiers. Invalid value: {v}")

        sql = f"""
        SELECT * 
        FROM cypher('production_graph', $$
            MATCH (a:{from_label} {{{from_key}: %s}}), (b:{to_label} {{{to_key}: %s}})
            CREATE (a)-[r:{edge_type}]->(b)
            RETURN r
        $$) AS (edge agtype);
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, (from_value, to_value))
            result = cur.fetchone()
            return result[0]['edge']  # Return the edge properties
    

    def get_edges(
            self, 
            from_label: Optional[str] = None, 
            from_id: Optional[tuple[str, int]] = None,
            to_label: Optional[str] = None, 
            to_id: Optional[tuple[str, int]] = None,
            edge_type: Optional[str] = None
        ) -> list[dict]:
        """
        Fetch edges matching criteria.
        Args:
            from_label (Optional[str]): Label of the starting node.
            from_id (Optional[tuple[str, int]]): (property_key, property_value) of the starting node.
            to_label (Optional[str]): Label of the ending node.
            to_id (Optional[tuple[str, int]]): (property_key, property_value) of the ending node.
            edge_type (Optional[str]): Type of the edge.
        """
        params = []

        match_clause = "MATCH (a)-[r]->(b)"  # always match all edges first
        conditions = []

        for label in [from_label, to_label]:
            if label and not label.isidentifier():
                raise ValueError(f"Node labels must be valid identifiers. Invalid label: {label}")
        if edge_type and not edge_type.isidentifier():
            raise ValueError(f"Edge type must be a valid identifier. Invalid edge type: {edge_type}")
        if from_id:
            prop_name, _ = from_id
            if not prop_name.isidentifier():
                raise ValueError(f"Property key must be a valid identifier. Invalid key: {prop_name}")
        if to_id:
            prop_name, _ = to_id
            if not prop_name.isidentifier():
                raise ValueError(f"Property key must be a valid identifier. Invalid key: {prop_name}")

        # labels
        if from_label:
            match_clause = f"MATCH (a:{from_label})-[r]->(b)"
        if to_label:
            match_clause = f"MATCH (a)-[r]->(b:{to_label})"
        
        # IDs
        if from_id:
            prop_name, value = from_id
            conditions.append(f"a.{prop_name} = %s")
            params.append(value)
        if to_id:
            prop_name, value = to_id
            conditions.append(f"b.{prop_name} = %s")
            params.append(value)

        # Edge type
        if edge_type:
            conditions.append(f"type(r) = '{edge_type}'")  # edge type filtering in WHERE

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        sql = f"""
        SELECT * 
        FROM cypher('production_graph', $$
            {match_clause}
            {where_clause}
            RETURN r
        $$) AS (edge agtype);
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            rows = cur.fetchall()
            return [row[0]['edge'] for row in rows]  # Return list of edge properties
            

    def delete_edge(
            self,
            from_label: str,
            from_id: tuple[str,int],
            to_label: str,
            to_id: tuple[str,int],
            edge_type: Optional[str] = None
        ) -> None:
        """
        Delete a specific edge.
        Args:
            from_label (str): Label of the starting node.
            from_id (tuple[str, int]): (property_key, property_value) of the starting node.
            to_label (str): Label of the ending node.
            to_id (tuple[str, int]): (property_key, property_value) of the ending node.
            edge_type (Optional[str]): Type of the edge.
        """

        from_key, from_value = from_id
        to_key, to_value = to_id

        for v in [from_key, to_key, edge_type, from_label, to_label]:
            if not v.isidentifier():
                raise ValueError(f"Property keys and edge type must be valid identifiers. Invalid value: {v}")

        conditions = [f"a.{from_key} = %s", f"b.{to_key} = %s"]
        params = [from_value, to_value]

        # Edge type filtering
        if edge_type:
            conditions.append(f"type(r) = '{edge_type}'")

        where_clause = "WHERE " + " AND ".join(conditions)
        
        sql = f"""
        SELECT *
        FROM cypher('production_graph', $$
            MATCH (a:{from_label})-[r]->(b:{to_label})
            {where_clause}
            DELETE r
        $$) AS (count agtype);
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            # No need to fetch results for this operation


    # Specialized Operations
    def rebuild_next_operation_edges(self, product_id: int) -> None:
        """Rebuild NEXT_OPERATION edges based on OpStep sequences."""

        if not isinstance(product_id, int):
            raise ValueError("product_id must be an integer.")
        
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

    def rebuild_can_run_on_edges(self) -> None:
        """
        Rebuild CAN_RUN_ON edges for all operations based on required_machine_type.
        """

        sql = """
        SELECT *
        FROM cypher('production_graph', $$
            MATCH (op:Operation)-[r:CAN_RUN_ON]->()
            DELETE r;

            MATCH (op:Operation), (m:Machine)
            WHERE op.required_machine_type = m.type
            CREATE (op)-[:CAN_RUN_ON]->(m)
            RETURN count(*)
        $$) AS (count agtype);
        """
        with self.conn.cursor() as cur:
            cur.execute(sql)

    def rebuild_uses_edges(self) -> None:
        """
        Rebuild USES edges for all operations based on material_needed property.
        """
        
        sql = """
        SELECT *
        FROM cypher('production_graph', $$
            MATCH (op:Operation)-[r:USES]->()
            DELETE r;

            MATCH (op:Operation), (mat:Material)
            WHERE op.material_needed = mat.material_id
            CREATE (op)-[:USES]->(mat)
            RETURN count(*)
        $$) AS (count agtype);
        """

        with self.conn.cursor() as cur:
            cur.execute(sql)