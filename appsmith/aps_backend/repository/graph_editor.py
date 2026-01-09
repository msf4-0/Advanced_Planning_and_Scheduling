from typing_extensions import Optional
from repository import DBTable
import json
import logging


class GraphEditor:
    def __init__(self, table: DBTable):
        self.table = table

    def get_table(self) -> DBTable:
        return self.table

    # Node Operations
    def create_node(
            self, 
            label: str, 
            properties: dict, 
            conn = None
        ) -> dict:
        """
        Create a node with the given label and properties.

        Args:
            label (str): The label of the node.
            properties (dict): A dictionary of properties for the node.

        Returns:
            dict: The created node's properties.
        """
        close_conn = False
        if conn is None:
            conn = self.table.get_connection()
            close_conn = True

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
            RETURN id(n) AS id, properties(n) AS props
        $$) AS (id agtype, props agtype);
        """

        cur = conn.cursor()
        
        try:
            logging.info("[GraphEditor.create_node] Executing node creation.")
            logging.info(f"SQL: {sql.strip()}")
            logging.info(f"Params: {tuple(properties.values())}")

            cur.execute(sql, tuple(properties.values()))
            
            result = cur.fetchone()

            if not result:
                logging.error("No result returned from cypher CREATE.")
                return {}
            
            return {
                "id": json.loads(result[0]),
                **json.loads(result[1])
            }  # Return the node properties

        except Exception as e:
            logging.exception(f"Exception: {e}")
            return {}
        finally:
            logging.info("[GraphEditor.create_node] Finished node creation attempt.")
            cur.close()
            if close_conn:
                conn.commit()
                conn.close()
        

    def get_node(
            self,
            label: str, 
            filters: dict,
            conn = None
        ) -> list[dict]:
        """
        Retrieve nodes with the given label and optional filters.

        Args:
            label (str): The label of the node.
            filters (dict): A dictionary of properties to filter by.

        Returns:
            list[dict]: A list of nodes matching the criteria.
        """

        close_conn = False
        if conn is None:
            conn = self.table.get_connection()
            close_conn = True

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
            $$) AS (id agtype, props agtype);
            """
            params = tuple(filters.values())
        else:
            sql = f"""
            SELECT * 
            FROM cypher('production_graph', $$
                MATCH (n:{label})
                RETURN id(n) AS id, properties(n) AS props
            $$) AS (id agtype, props agtype);
            """
            params = ()

        cur = conn.cursor()

        try:
            cur.execute(sql, params)
            
            rows = cur.fetchall()
        
            return [
                {
                    "id": row[0], 
                    **json.loads(row[1])
                }
                for row in rows
            ]  # Return list of node properties
        
        finally:
            cur.close()
            if close_conn:
                conn.commit()
                conn.close()
        

    def update_node(
            self, 
            node_id: int, 
            properties: dict,
            conn = None
        ) -> dict:
        """
        Update a node's properties.

        Args:
            label (str): The label of the node.
            node_id (tuple[str, int]): A tuple of (property_key, property_value) to identify the node.
            properties (dict): A dictionary of properties to update.

        Returns:
            dict: The updated node's properties.
        """

        close_conn = False
        if conn is None:
            conn = self.table.get_connection()
            close_conn = True

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
        $$) AS (id agtype, props agtype);
        """

        cur = conn.cursor()

        try:
            cur.execute(sql, (node_id, *properties.values()))
            
            result = cur.fetchone()
            if not result:
                raise ValueError(f"No node found with id {node_id}.")
            
            return {
                "id": result[0], 
                **json.loads(result[1])
                }  # Return the updated node properties

        finally:
            cur.close()
            if close_conn:
                conn.commit()
                conn.close()


    def delete_node(
            self, 
            node_id: int,
            conn = None
        ) -> None:
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

        close_conn = False
        if conn is None:
            conn = self.table.get_connection()
            close_conn = True

        cur = conn.cursor()

        try:
            cur.execute(sql, (node_id,))
            # No need to fetch results for this operation

        finally:
            cur.close()
            if close_conn:
                conn.commit()   
                conn.close()
    
    # Edge Operations
    def create_edge(
            self, 
            from_id: int, 
            to_id: int, 
            edge_type: str,
            conn = None
        ) -> dict:
        """
        Create an edge of given type between two nodes.
        Args:
            from_id (int): Node ID of the starting node.
            to_id (int): Node ID of the ending node.
            edge_type (str): Type of the edge.

        Returns:
            dict: The created edge's properties.
        """
        
        sql = f"""
        SELECT * 
        FROM cypher('production_graph', $$
            MATCH (a), (b)
            WHERE id(a) = {from_id} AND id(b) = {to_id}
            CREATE (a)-[r:{edge_type}]->(b)
            RETURN r
        $$) AS (edge agtype);
        """

        close_conn = False
        if conn is None:
            conn = self.table.get_connection()
            close_conn = True

        cur = conn.cursor()

        try:
            logging.info("[GraphEditor.create_edge] Executing edge creation.")
            cur.execute(sql)
            logging.info("Raw SQL:\n" + sql)

            edges = self.get_edges(
                from_id=from_id, 
                to_id=to_id,
                edge_type=edge_type,
                conn=conn
                )

            return edges[0] if edges else {}  # Return the first matching edge or empty dict

        finally:
            logging.info("[GraphEditor.create_edge] Finished edge creation attempt.")
            cur.close()
            if close_conn:
                conn.commit()
                conn.close()

    def get_edges(
            self, 
            from_id: Optional[int] = None, 
            to_id: Optional[int] = None, 
            edge_type: Optional[str] = None,
            conn = None
        ) -> list[dict]:
        """
        Fetch edges matching criteria.
        Args:
            from_id (Optional[int]): Node ID of the starting node.
            to_id (Optional[int]): Node ID of the ending node.
            edge_type (Optional[str]): Type of the edge.
        """

        match_clause = "MATCH (a)-[r]->(b)"  # always match all edges first
        conditions = []

        # Filter by Node IDs
        if from_id is not None:
            conditions.append(f"id(a) = {from_id}")
        if to_id is not None:
            conditions.append(f"id(b) = {to_id}")

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

        close_conn = False
        if conn is None:
            conn = self.table.get_connection()
            close_conn = True

        cur = conn.cursor()

        try:
            logging.info("[GraphEditor.get_edges] Executing edge retrieval. Edge Type: %s", edge_type)
            # logging.info(f"SQL: {sql.strip()}")
            
            cur.execute(sql)
            
            rows = cur.fetchall()

            if not rows:
                logging.info("[GraphEditor.get_edges] No edges found matching criteria.")
                return []
            
            parsed_edges = []
            for row in rows:
                edge_str = row[0]
                # Remove ::edge suffix if present
                if isinstance(edge_str, str) and edge_str.endswith("::edge"):
                    edge_str = edge_str[:-6]
                try:
                    edge_dict = json.loads(edge_str)
                    parsed_edges.append(edge_dict)
                except json.JSONDecodeError as e:
                    logging.error(f"Failed to parse edge JSON: {e}")

            # logging.info(f"Retrieved: {rows}")
            logging.info(f"Parsed Edges: {parsed_edges}")
            return parsed_edges  # Return list of parsed edge properties
        finally:
            logging.info("[GraphEditor.get_edges] Finished edge retrieval attempt.")
            cur.close()
            if close_conn:
                conn.commit()
                conn.close()

    def delete_edge(
            self, 
            from_id: int, 
            to_id: int, 
            edge_type: Optional[str] = None,
            conn = None
        ) -> None:
        """
        Delete a specific edge.
        Args:
            from_label (str): Label of the starting node.
            from_id (tuple[str, int]): (property_key, property_value) of the starting node property.
            to_label (str): Label of the ending node.
            to_id (tuple[str, int]): (property_key, property_value) of the ending node property.
            edge_type (Optional[str]): Type of the edge.
        """

        conditions = [f"a.id = {from_id}", f"b.id = {to_id}"]

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

        close_conn = False
        if conn is None:
            conn = self.table.get_connection()
            close_conn = True

        cur = conn.cursor()

        try:
            cur.execute(sql)
            
            # No need to fetch results for this operation

        finally:
            cur.close()
            if close_conn:
                conn.commit()
                conn.close()