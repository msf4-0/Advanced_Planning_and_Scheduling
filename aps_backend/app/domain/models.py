"""Domain entity dataclasses.

These are deliberately free of FastAPI, psycopg, SQLAlchemy, and OR-Tools
imports. They are the shared vocabulary for the API, scheduling, and adapter
layers.
"""

from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Optional

from .enums import OperationStatus, ResourceType, WorkOrderStatus


@dataclass
class WorkOrder:
    """Customer/manufacturing demand that anchors operations."""

    id: str
    target_item_id: str
    quantity_to_make: int
    due_date: datetime
    status: WorkOrderStatus = WorkOrderStatus.DRAFT


@dataclass
class Operation:
    """A single processing step within a work order."""

    id: str
    work_order_id: str
    sequence_number: int
    duration_minutes: int
    assigned_resource_id: Optional[str] = None
    status: OperationStatus = OperationStatus.DRAFT


@dataclass
class Resource:
    """A machine, human, or tooling resource."""

    id: str
    name: str
    resource_type: ResourceType = ResourceType.MACHINE
    is_active: bool = True


@dataclass
class Material:
    """Raw material stock and its earliest availability time."""

    id: str
    name: str
    quantity_available: float = 0.0
    available_date_minutes: int = 0


@dataclass
class Item:
    """Finished-product master data."""

    id: str
    name: str
    sku: str


@dataclass
class RoutingTemplate:
    """Blueprint step used to generate operations for a new work order."""

    target_item_id: str
    step_sequence: int
    required_resource_type: ResourceType
    standard_duration_minutes: int
    id: Optional[int] = None


@dataclass
class OperationDependency:
    """Directed edge between two operations (upstream must finish first)."""

    upstream_op_id: str
    downstream_op_id: str


@dataclass
class OperationMaterial:
    """Bill-of-materials requirement for one operation."""

    operation_id: str
    material_id: str
    quantity_required: float


@dataclass
class FactoryShift:
    """Weekly working-time window for a resource."""

    resource_id: str
    day_of_week: int
    start_time: time
    end_time: time
    id: Optional[int] = None


@dataclass
class FactoryHoliday:
    """Global factory closure date."""

    holiday_date: date
    description: Optional[str] = None
    id: Optional[int] = None
