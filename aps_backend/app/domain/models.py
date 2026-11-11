"""Domain entity dataclasses.

These are deliberately free of FastAPI, psycopg, SQLAlchemy, and OR-Tools
imports. They are the shared vocabulary for the API, scheduling, and adapter
layers.
"""

from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Optional

from .enums import OperationStatus, ResourceType, WorkOrderStatus
from .errors import ValidationError


@dataclass(frozen=True)
class WorkOrder:
    """Customer/manufacturing demand that anchors operations."""

    id: str
    target_item_id: str
    quantity_to_make: int
    due_date: datetime
    status: WorkOrderStatus = WorkOrderStatus.DRAFT

    def __post_init__(self) -> None:
        if self.quantity_to_make <= 0:
            raise ValidationError(
                "Work order quantity_to_make must be greater than zero."
            )


@dataclass(frozen=True)
class Operation:
    """A single processing step within a work order."""

    id: str
    work_order_id: str
    sequence_number: int
    duration_minutes: int
    assigned_resource_id: Optional[str] = None
    status: OperationStatus = OperationStatus.DRAFT

    def __post_init__(self) -> None:
        if self.duration_minutes <= 0:
            raise ValidationError(
                "Operation duration_minutes must be greater than zero."
            )


@dataclass(frozen=True)
class Resource:
    """A machine, human, or tooling resource."""

    id: str
    name: str
    resource_type: ResourceType = ResourceType.MACHINE
    is_active: bool = True


@dataclass(frozen=True)
class Material:
    """Raw material stock and its earliest availability time."""

    id: str
    name: str
    quantity_available: float = 0.0
    available_date_minutes: int = 0

    def __post_init__(self) -> None:
        if self.quantity_available < 0:
            raise ValidationError("Material quantity_available cannot be negative.")
        if self.available_date_minutes < 0:
            raise ValidationError("Material available_date_minutes cannot be negative.")


@dataclass(frozen=True)
class Item:
    """Finished-product master data."""

    id: str
    name: str
    sku: str


@dataclass(frozen=True)
class RoutingTemplate:
    """Blueprint step used to generate operations for a new work order."""

    target_item_id: str
    step_sequence: int
    required_resource_type: ResourceType
    standard_duration_minutes: int
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if self.step_sequence <= 0:
            raise ValidationError("Routing step_sequence must be greater than zero.")
        if self.standard_duration_minutes <= 0:
            raise ValidationError(
                "Routing standard_duration_minutes must be greater than zero."
            )


@dataclass(frozen=True)
class OperationDependency:
    """Directed edge between two operations (upstream must finish first)."""

    upstream_op_id: str
    downstream_op_id: str


@dataclass(frozen=True)
class OperationMaterial:
    """Bill-of-materials requirement for one operation."""

    operation_id: str
    material_id: str
    quantity_required: float

    def __post_init__(self) -> None:
        if self.quantity_required <= 0:
            raise ValidationError(
                "Operation material quantity_required must be greater than zero."
            )


@dataclass(frozen=True)
class FactoryShift:
    """Weekly working-time window for a resource."""

    resource_id: str
    day_of_week: int
    start_time: time
    end_time: time
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if not 1 <= self.day_of_week <= 7:
            raise ValidationError("Factory shift day_of_week must be between 1 and 7.")
        if self.start_time >= self.end_time:
            raise ValidationError("Factory shift start_time must be before end_time.")


@dataclass(frozen=True)
class FactoryHoliday:
    """Global factory closure date."""

    holiday_date: date
    description: Optional[str] = None
    id: Optional[int] = None
