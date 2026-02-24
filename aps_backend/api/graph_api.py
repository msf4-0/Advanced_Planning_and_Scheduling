from fastapi import APIRouter, Body, HTTPException, Query
from typing_extensions import List
from typing import Dict

from repository import DBTable, GraphEditor
from schema_mapper import SchemaMapper

router = APIRouter()

@router.get(
    "/node-names",
    response_model=List[Dict],
    tags=["Graph General"]
)
def get_graph_nodes():
    '''
    Fetch all nodes from a specified graph in Apache AGE.

    Location: appsmith/aps_backend/api/graph_api.py
    '''


    
    try:
        db = DBTable()
        mapper = SchemaMapper(db.get_connection_graph())
        graph = GraphEditor(db)

        nodes = mapper.list_graph_labels()
        return nodes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post(
    "/new-path",
    response_model=List[Dict],
    tags=["Graph General"]
)
def add_new_graph_path(
    nodes: list[dict] = Body(...),
    edges: list[dict] = Body(...)
):
    '''
    Add a new path to the graph in Apache AGE.

    Location: appsmith/aps_backend/api/graph_api.py
    '''
    try:
        db = DBTable()
        mapper = SchemaMapper(db.get_connection_graph())
        graph = GraphEditor(db)

        node_ids = {}
        # Add nodes: nodes = [ {"label": ..., "properties": ..., "temp_id": ...}, ... ]
        for node in nodes:
            label = node.get("label")
            properties = node.get("properties")
            temp_id = node.get("temp_id")

            if not label or not isinstance(properties, dict) or not temp_id:
                raise HTTPException(status_code=400, detail="Each node must have 'label', 'properties' (dict), and 'temp_id' (unique string)")
            
            created_id = graph.create_node(
                label=label,
                properties=properties,
                conn=None
            )
            
            node_ids[temp_id] = created_id  # Use temp_id for edge reference

        # Add edges: edges = [ {"edge_type": ..., "from": ..., "to": ...}, ... ]
        for edge in edges:
            edge_type = edge.get("edge_type")
            from_temp = edge.get("from")
            to_temp = edge.get("to")
            if not edge_type or not from_temp or not to_temp:
                raise HTTPException(status_code=400, detail="Each edge must have 'edge_type', 'from', and 'to' (temp_id references)")
            from_node_id = node_ids.get(from_temp)
            to_node_id = node_ids.get(to_temp)
            if from_node_id and to_node_id:
                graph.create_edge(
                    from_id=from_node_id,
                    to_id=to_node_id,
                    edge_type=edge_type,
                    conn=None
                )
            else:
                raise HTTPException(status_code=400, detail=f"Node temp_id(s) '{from_temp}' or '{to_temp}' not found in nodes.")

        return {"success": True, "message": "Path added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    