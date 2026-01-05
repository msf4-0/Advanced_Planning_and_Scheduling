from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import date, datetime
from psycopg2.extras import execute_values
'''
from repository.db_repository import get_connection, save_schedule, add_order, fetch_orders, fetch_operations, fetch_machines, log_schedule_run, save_schedule_archive, fetch_inventory_for_item
from service.scheduler import generate_schedule, pick_machine
from routes import RouteService, RouteRepository
from models import InventoryItem, OrderRead, OrderCreate, ScheduledOperation
'''

from api import (
    machine_api,
    operation_api,
    order_api,
    inventory_api,
    product_api,
    blueprint_api,
    schedule_api,
)

import os
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