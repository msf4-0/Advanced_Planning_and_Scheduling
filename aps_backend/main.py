from fastapi import FastAPI
from repository import DBTable

from api import (
    admin_api,
    aps_api,
    graph_api,
    table_api
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

app.include_router(aps_api.router)
app.include_router(admin_api.router)
app.include_router(graph_api.router)
app.include_router(table_api.router)