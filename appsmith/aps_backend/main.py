from fastapi import FastAPI

from api import (
    machine_api,
    operation_api,
    order_api,
    inventory_api,
    product_api,
    blueprint_api,
    schedule_api,
)

import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

app.include_router(machine_api.router)
app.include_router(operation_api.router)
app.include_router(order_api.router)
app.include_router(inventory_api.router)
app.include_router(product_api.router)
app.include_router(blueprint_api.router)
app.include_router(schedule_api.router)