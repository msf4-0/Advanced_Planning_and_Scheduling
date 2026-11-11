"""Row-to-domain mappers.

The current repository returns psycopg2 ``RealDictCursor`` rows (mappings of
column name to value). These functions translate those rows into the domain
dataclasses without leaking SQLAlchemy/psycopg types into the domain layer.

The mappers are strict about required fields and enum values: corrupt or
unexpected database state raises a domain ``ValidationError`` rather than
silently substituting a default that would change scheduling behavior.
"""

from collections.abc import Mapping
from enum import Enum
from typing import Any, TypeVar

from app.domain.errors import ValidationError
from app.domain.models import (
    FactoryHoliday,
    FactoryShift,
    Item,
    Material,
    Operation,
    OperationDependency,
    OperationMaterial,
    Resource,
    RoutingTemplate,
    WorkOrder,
)
from app.domain.enums import (
    OperationStatus,
    ResourceType,
    WorkOrderStatus,
)

EnumType = TypeVar("EnumType", bound=Enum)


def _required(row: Mapping[str, Any], key: str) -> Any:
    value = row.get(key)
    if value is None:
        raise ValidationError(f"Row is missing required field '{key}'.")
    return value


def _optional_int(row: Mapping[str, Any], key: str) -> int | None:
    value = row.get(key)
    return None if value is None else int(value)


def _enum(
    enum_type: type[EnumType],
    value: Any,
    default: EnumType,
) -> EnumType:
    if value is None:
        return default
    try:
        return enum_type(value)
    except ValueError as exc:
        raise ValidationError(
            f"Unknown {enum_type.__name__} value {value!r}."
        ) from exc


def row_to_work_order(row: Mapping[str, Any]) -> WorkOrder:
    return WorkOrder(
        id=str(_required(row, "id")),
        target_item_id=str(_required(row, "target_item_id")),
        quantity_to_make=int(_required(row, "quantity_to_make")),
        due_date=_required(row, "due_date"),
        status=_enum(WorkOrderStatus, row.get("status"), WorkOrderStatus.DRAFT),
    )


def row_to_operation(row: Mapping[str, Any]) -> Operation:
    assigned_resource_id = row.get("assigned_resource_id")
    return Operation(
        id=str(_required(row, "id")),
        work_order_id=str(_required(row, "work_order_id")),
        sequence_number=int(_required(row, "sequence_number")),
        duration_minutes=int(_required(row, "duration_minutes")),
        assigned_resource_id=(
            None if assigned_resource_id is None else str(assigned_resource_id)
        ),
        status=_enum(OperationStatus, row.get("status"), OperationStatus.DRAFT),
    )


def row_to_resource(row: Mapping[str, Any]) -> Resource:
    is_active = row.get("is_active")
    return Resource(
        id=str(_required(row, "id")),
        name=str(_required(row, "name")),
        resource_type=_enum(
            ResourceType,
            row.get("resource_type"),
            ResourceType.MACHINE,
        ),
        is_active=True if is_active is None else bool(is_active),
    )


def row_to_material(row: Mapping[str, Any]) -> Material:
    return Material(
        id=str(_required(row, "id")),
        name=str(_required(row, "name")),
        quantity_available=float(row.get("quantity_available") or 0.0),
        available_date_minutes=int(row.get("available_date_minutes") or 0),
    )


def row_to_item(row: Mapping[str, Any]) -> Item:
    return Item(
        id=str(_required(row, "id")),
        name=str(_required(row, "name")),
        sku=str(_required(row, "sku")),
    )


def row_to_routing_template(row: Mapping[str, Any]) -> RoutingTemplate:
    return RoutingTemplate(
        target_item_id=str(_required(row, "target_item_id")),
        step_sequence=int(_required(row, "step_sequence")),
        required_resource_type=_enum(
            ResourceType,
            _required(row, "required_resource_type"),
            ResourceType.MACHINE,
        ),
        standard_duration_minutes=int(_required(row, "standard_duration_minutes")),
        id=_optional_int(row, "id"),
    )


def row_to_operation_dependency(row: Mapping[str, Any]) -> OperationDependency:
    return OperationDependency(
        upstream_op_id=str(_required(row, "upstream_op_id")),
        downstream_op_id=str(_required(row, "downstream_op_id")),
    )


def row_to_operation_material(row: Mapping[str, Any]) -> OperationMaterial:
    return OperationMaterial(
        operation_id=str(_required(row, "operation_id")),
        material_id=str(_required(row, "material_id")),
        quantity_required=float(_required(row, "quantity_required")),
    )


def row_to_factory_shift(row: Mapping[str, Any]) -> FactoryShift:
    return FactoryShift(
        resource_id=str(_required(row, "resource_id")),
        day_of_week=int(_required(row, "day_of_week")),
        start_time=_required(row, "start_time"),
        end_time=_required(row, "end_time"),
        id=_optional_int(row, "id"),
    )


def row_to_factory_holiday(row: Mapping[str, Any]) -> FactoryHoliday:
    return FactoryHoliday(
        holiday_date=_required(row, "holiday_date"),
        description=row.get("description"),
        id=_optional_int(row, "id"),
    )
