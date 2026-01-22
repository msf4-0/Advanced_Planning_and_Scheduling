from fastapi import APIRouter, Body, HTTPException, Query
from typing_extensions import List
from typing import Dict

from repository import DBTable, GraphEditor
from schema_mapper import SchemaMapper

router = APIRouter()
db = DBTable()
mapper = SchemaMapper(db.get_connection())
graph = GraphEditor(db)

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
        nodes = mapper.list_graph_labels()
        return nodes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

