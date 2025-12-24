from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date, datetime

class OperationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    operation_id: int
    name: str
    duration: int

class OpStepRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    sequence: int
    operation: OperationRead

class ProductRouteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    product_name: str
    steps: List[OpStepRead]

class RouteFilter(BaseModel):
    min_sequence: Optional[int] = None
    max_sequence: Optional[int] = None
    operation_id: Optional[int] = None


class OpStepCreate(BaseModel):
    product_id: int
    operation_id: int
    insert_after: Optional[int] = None  # sequence number after which to insert the new step

class ReorderSteps(BaseModel):
    new_order: List[int]  # List of operation_ids in the desired order