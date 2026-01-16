from fastapi import FastAPI
from repository import DBTable

from api import (
    machine_api,
    operation_api,
    order_api,
    inventory_api,
    product_api,
    blueprint_api,
    schedule_api,
    material_api,
    manufacturing_api,
    constraint_api
)

import logging

db = DBTable()

app = FastAPI()
logging.basicConfig(level=logging.INFO)

@app.get(
    "/get/count/{table_name}",
    tags=["Utility"]
    )
def get_table_count(table_name: str):
    '''
    Get the count of records in a specified table.

    Location: appsmith/aps_backend/main.py
    '''
    count = db.fetch_counts(table_name)
    return {"table_name": table_name, "count": count}

app.include_router(material_api.router)
app.include_router(inventory_api.router)
app.include_router(product_api.router)
app.include_router(machine_api.router)
app.include_router(operation_api.router)
app.include_router(order_api.router)
app.include_router(manufacturing_api.router)
app.include_router(blueprint_api.router)
app.include_router(schedule_api.router)
app.include_router(constraint_api.router)