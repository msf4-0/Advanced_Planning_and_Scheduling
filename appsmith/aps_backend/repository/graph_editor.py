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
            return {
                "id": result[0]["id"],
                **result[0]["props"]
            }  # Return the node properties
        

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
                RETURN id(n) AS id, properties(n) AS props
            $$) AS (node agtype);
            """
            params = tuple(filters.values())
        else:
            sql = f"""
            SELECT * 
            FROM cypher('production_graph', $$
                MATCH (n:{label})
                RETURN id(n) AS id, properties(n) AS props
            $$) AS (node agtype);
            """
            params = ()

        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            return [
                {"id": row[0], **row[1]["props"]}
                for row in rows
            ]  # Return list of node properties
        

    def update_node(self, label: str, node_id: int, properties: dict) -> dict:
        """
        Update a node's properties.

        Args:
            label (str): The label of the node.
            node_id (tuple[str, int]): A tuple of (property_key, property_value) to identify the node.
            properties (dict): A dictionary of properties to update.

        Returns:
            dict: The updated node's properties.
        """

        if not properties:
            raise ValueError("Properties to update cannot be empty.")
        
        for key in properties.keys():
            if not isinstance(key, str):
                raise ValueError("All property keys must be strings.")

        set_str = ', '.join(f"n.{k} = %s" for k in properties.keys())
        sql = f"""
        SELECT * 
        FROM cypher('production_graph', $$
            MATCH (n)
            WHERE id(n) = %s
            SET {set_str}
            RETURN id(n) AS id, properties(n) AS props
        $$) AS (id bigint, props agtype);
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, (node_id, *properties.values()))
            result = cur.fetchone()
            if not result:
                raise ValueError(f"No node found with id {node_id}.")
            
            return {"id": result[0], **result[1]["props"]}  # Return the updated node properties


    def delete_node(self, node_id: int) -> None:
        """
        Delete a node with the given label and property.

        Args:
            label (str): The label of the node.
            property_key (str): The property key to identify the node.
            property_value: The property value to identify the node.
        """
        
        sql = f"""
        SELECT * 
        FROM cypher('production_graph', $$
            MATCH (n)
            WHERE id(n) = %s
            DETACH DELETE n
        $$) AS (count agtype);
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, (node_id,))
            # No need to fetch results for this operation

    
    # Edge Operations
    def create_edge(self, from_id: int, to_id: int, edge_type: str) -> dict:
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
        
        sql = f"""
        SELECT * 
        FROM cypher('production_graph', $$
            MATCH (a), (b)
            WHERE id(a) = %s AND id(b) = %s
            CREATE (a)-[r:{edge_type}]->(b)
            RETURN r
        $$) AS (edge agtype);
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, (from_id, to_id))
            result = cur.fetchone()
            return result[0]['edge']  # Return the edge properties
    

    def get_edges(self, from_id: Optional[int] = None, to_id: Optional[int] = None, edge_type: Optional[str] = None) -> list[dict]:
        """
        Fetch edges matching criteria.
        Args:
            from_id (Optional[int]): ID of the starting node.
            to_id (Optional[int]): ID of the ending node.
            edge_type (Optional[str]): Type of the edge.
        """

        match_clause = "MATCH (a)-[r]->(b)"  # always match all edges first
        conditions = []
        params = []

        # Filter by Node IDs
        if from_id is not None:
            conditions.append(f"a.id = %s")
            params.append(from_id)
        if to_id is not None:
            conditions.append(f"b.id = %s")
            params.append(to_id)
        
        # Filter by Edge Type

        # Edge type
        if edge_type:
            if not edge_type.isidentifier():
                raise ValueError(f"Edge type must be a valid identifier. Invalid edge type: {edge_type}")
            conditions.append(f"type(r) = '{edge_type}'")  # edge type filtering in WHERE

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

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
            

    def delete_edge(self, from_id: int, to_id: int, edge_type: Optional[str] = None) -> None:
        """
        Delete a specific edge.
        Args:
            from_label (str): Label of the starting node.
            from_id (tuple[str, int]): (property_key, property_value) of the starting node.
            to_label (str): Label of the ending node.
            to_id (tuple[str, int]): (property_key, property_value) of the ending node.
            edge_type (Optional[str]): Type of the edge.
        """

        conditions = [f"a.id = %s", f"b.id = %s"]
        params = [from_id, to_id]

        # Edge type filtering
        if edge_type:
            if not edge_type.isidentifier():
                raise ValueError(f"Edge type must be a valid identifier. Invalid edge type: {edge_type}")
            conditions.append(f"type(r) = '{edge_type}'")  # edge type filtering in WHERE

        where_clause = f"WHERE {' AND '.join(conditions)}"
        
        sql = f"""
        SELECT *
        FROM cypher('production_graph', $$
            MATCH (a)-[r]->(b)
            {where_clause}
            DELETE r
        $$) AS (count agtype);
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            # No need to fetch results for this operation
