from fastapi import APIRouter, Body, Query, HTTPException
from repository import DBTable, GraphEditor
from service import MaterialService
from typing_extensions import List
from typing import Optional

router = APIRouter()

@router.get(
    "/get/materials/",
    response_model=List[dict],
    tags=["Materials"]
)
def get_materials(
    material_id: Optional[int] = Query(None), 
    material_name: Optional[str] = Query(None)
    ):
    '''
    Fetch the list of materials from the database.
    or fetch a specific material by its ID or name.

    Location: appsmith/aps_backend/api/material_api.py
    '''
    service = MaterialService(DBTable())
    materials = service.fetch_material(
        material_id=material_id, 
        material_name=material_name
    )

    return materials

@router.post(
    "/add/material",
    response_model=dict,
    status_code=201,
    tags=["Materials"]
)
def add_material(material_name: str = Body(...)):
    '''
    Add a new material to the database.

    Location: appsmith/aps_backend/api/material_api.py
    '''
    
    service = MaterialService(DBTable())
    try:
        material_id, existed = service.add_material(material_name=material_name)
    
        return {
            "material_id": material_id,
            "material_name": material_name,
            "existed": existed
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post(
    "/generate/material_node/{material_id}",
    status_code=201,
    tags=["Materials"]
)
def generate_material_node(material_id: int):
    '''
    Generate a material node for the given material ID.

    Location: appsmith/aps_backend/api/material_api.py
    '''
    service = MaterialService(DBTable())

    try:
        
        new_node = service.generate_material_node(material_id=material_id)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "material node generated", "node": new_node}

@router.post(
    "/regenerate-all-material-nodes",
    status_code=201,
    tags=["Materials"]
)
def regenerate_all_material_nodes():
    '''
    Regenerate all material nodes in the graph database.

    Location: appsmith/aps_backend/api/material_api.py
    '''
    service = MaterialService(DBTable())

    materials = service.fetch_material()

    failed_materials = []

    for material in materials:
        material_id = material['material_id']
        try:
            service.generate_material_node(material_id=material_id)
        except Exception as e:
            failed_materials.append({
                "material_id": material_id,
                "error": str(e)
            })

    if failed_materials:
        return {
            "status": "completed with errors",
            "failed_materials": failed_materials
        }

    return {"status": "all material nodes generated successfully"}