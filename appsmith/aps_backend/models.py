
from pydantic import BaseModel, ConfigDict, field_validator
from typing_extensions import List, Optional, TypedDict
from datetime import datetime, timezone

# AGE Graph Models
class ManufacturingStep(TypedDict):
    operation_id: int
    sequence: int
    depends_on: List[int]

class ProductRouteCreate(BaseModel):
    """
    Model for creating a new product route.
    Attributes:
        product_id (int): ID of the product.
        manufacturing_line (List[Tuple[int, int]]): List of tuples representing (operation_id, sequence).
    """
    product_id: int
    manufacturing_line : list[ManufacturingStep]  # List of dicts with 'operation_id', 'sequence', 'depends_on'

class ProductBlueprintRead(BaseModel):
    """
    Model representing the blueprint response for a product.
    Attributes:
        product_id (int): ID of the product.
        manufacturing_line (List[ManufacturingStep]): List of manufacturing steps.
    """
    product_id: int
    manufacturing_line: list[ManufacturingStep]

# ERD Models
class OperationRead(BaseModel):
    """
    Model representing an operation in the manufacturing process.

    Attributes:
        operation_id (int): Unique identifier for the operation.
        name (str): Name of the operation.
        duration (int): Duration of the operation in time units.
    """
    model_config = ConfigDict(from_attributes=True)

    operation_id: int
    name: str
    duration: int
    machine_type: int
    material_id: Optional[int] = None

class OpStepRead(BaseModel):
    """
    Model representing a step in the product route.
    Attributes:
        product_id (int): ID of the product this step belongs to.
        sequence (int): Sequence number of the step in the route.
        operation (OperationRead): The operation associated with this step.
    """
    model_config = ConfigDict(from_attributes=True)
    
    op_step_id: int
    order_id: int
    sequence_num: int
    operation: OperationRead

class RouteFilter(BaseModel):
    """
    Model for filtering routes based on sequence range or operation ID.
    Attributes:
        min_sequence (Optional[int]): Minimum sequence number to filter steps.
        max_sequence (Optional[int]): Maximum sequence number to filter steps.
        operation_id (Optional[int]): Specific operation ID to filter steps.
    """
    min_sequence: Optional[int] = None
    max_sequence: Optional[int] = None
    operation_id: Optional[int] = None


class OpStepCreate(BaseModel):
    """
    Model for creating a new operation step in a product route.
    Attributes:
        product_id (int): ID of the product to which the step will be added.
        operation_id (int): ID of the operation to be added as a step.
        insert_after (Optional[int]): Sequence number after which to insert the new step.
    """
    product_id: int
    operation_id: int
    insert_after: Optional[int] = None  # sequence number after which to insert the new step

class ReorderSteps(BaseModel):
    """
    Model for reordering operation steps in a product route.
    Attributes:
        new_order (List[int]): List of operation IDs in the desired order.
    """
    new_order: List[int]  # List of operation_ids in the desired order

class OrderCreate(BaseModel):
    """
    Model for creating a new order.
    Attributes:
        product_id (int): ID of the product being ordered.
        user_priority (int): Priority assigned by the user.
        due_date (date): Due date for the order.
        quantity (int): Quantity of the product ordered.
        priority (float): Internal priority used for scheduling.
    """
    product_id: int
    user_priority: int
    due_date: datetime
    quantity: int = 1
    priority: float = 0.0  # Internal priority used for scheduling

    @field_validator('due_date', mode='before')
    @classmethod
    def ensure_utc_due_date(cls, v):
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)

class OrderRead(OrderCreate):
    """
    Model for reading an order, including its unique identifier.
    Attributes:
        order_id (int): Unique identifier for the order.
    """
    order_id: int
    product_name: str
    status: str

    class Config:
        extra = "forbid"
    
    @field_validator('due_date', mode='before')
    @classmethod
    def ensure_utc_due_date(cls, v):
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)
        
class ScheduledOperation(BaseModel):
    """
    Model representing a scheduled operation in the production schedule.
    Attributes:
        order_id (int): ID of the order.
        operation (str): Name of the operation.
        machine (str): Machine assigned to the operation.
        start (int): Start time in hours.
        end (int): End time in hours.
    """
    order_id: int
    operation: str
    machine: str
    start: int
    end: int

class InventoryItem(BaseModel):
    """
    Model representing an inventory item.
    Attributes:
        item_id (int): Unique identifier for the inventory item.
        item_name (str): Name of the inventory item.
        quantity (int): Current quantity of the item in stock.
        min_required (int): Minimum required quantity for the item.
        max_capacity (int): Maximum capacity for the item in inventory.
    """
    item_id: int
    item_name: str
    quantity: int
    min_required: int
    max_capacity: int
    last_updated: datetime
    received_at: datetime
    material_id: Optional[int]
    age_days: int

# API Models

class ScheduleRequest(BaseModel):
    """
    Model for scheduling request parameters.
    Attributes:
        schedule_horizon (Optional[int]): Time horizon for scheduling in hours.
    """
    schedule_horizon: Optional[int] = None