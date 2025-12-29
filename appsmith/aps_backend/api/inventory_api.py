from fastapi import APIRouter, Body
from typing import List
from datetime import datetime

from repository.db_repository import DBTable
from models import InventoryItem

router = APIRouter()

@router.get("/get/inventory", response_model=List[InventoryItem])
def get_inventory():
    '''
    Fetch the current inventory items from the database.

    Location: appsmith/aps_backend/api/inventory_api.py
    '''
    db = DBTable()
    rows = db.fetch_inventory()
    inventory = [
        InventoryItem(
            item_id=row['item_id'],
            item_name=row['item_name'],
            quantity=row['quantity'],
            min_required=row['min_required'],
            max_capacity=row['max_capacity'],
            last_updated=row['last_updated'],
            received_at=row['received_at'],
            material_id=row.get('material_id'),
            age_days=(datetime.now() - row['received_at']).days
        )
        for row in rows
    ]

    return inventory

@router.post("/update/inventory")
def update_inventory(item_id: int = Body(...), quantity: int = Body(...)):
    '''
    Update the quantity of a specific inventory item.

    Location: appsmith/aps_backend/api/inventory_api.py
    '''
    db = DBTable()
    item_name = db.update_inventory_item(item_id, quantity)
    return {
        "status": "success", 
        "item_id": item_id, 
        "item_name": item_name,
        "new_quantity": quantity
    }

# @router.post("/update/inventory/{item_id}") # this endpoint is future implementation

@router.post("/add/inventory")
def add_inventory(
    item_name: str = Body(...), 
    quantity: int = Body(...), 
    min_required: int = Body(...), 
    max_capacity: int = Body(...)
):
    '''
    Add a new inventory item to the database.
    
    Location: appsmith/aps_backend/api/inventory_api.py
    '''
    db = DBTable()
    item_id = db.add_inventory_item(
        item_name=item_name, 
        quantity=quantity, 
        min_required=min_required, 
        max_capacity=max_capacity
    )
    return {
        "status": "success", 
        "item_id": item_id, 
        "item_name": item_name,
        "quantity": quantity
    }