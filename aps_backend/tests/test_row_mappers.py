"""Tests for psycopg2-row to domain-entity mappers."""

from datetime import date, datetime, time
from decimal import Decimal

import pytest

from app.adapters.db.mappers import (
    row_to_factory_holiday,
    row_to_factory_shift,
    row_to_item,
    row_to_material,
    row_to_operation,
    row_to_operation_dependency,
    row_to_operation_material,
    row_to_resource,
    row_to_routing_template,
    row_to_work_order,
)
from app.domain.enums import (
    OperationStatus,
    ResourceType,
    WorkOrderStatus,
)
from app.domain.errors import ValidationError


def test_work_order_mapping_parses_status_and_values():
    work_order = row_to_work_order(
        {
            "id": "WO-1",
            "target_item_id": "ITEM-1",
            "quantity_to_make": 10,
            "due_date": datetime(2026, 2, 1, 8, 0),
            "status": "Approved",
        }
    )

    assert work_order.id == "WO-1"
    assert work_order.quantity_to_make == 10
    assert work_order.status is WorkOrderStatus.APPROVED


def test_operation_mapping_handles_optional_resource_and_status():
    operation = row_to_operation(
        {
            "id": "OP-1",
            "work_order_id": "WO-1",
            "sequence_number": 10,
            "duration_minutes": 45,
            "assigned_resource_id": None,
            "status": "In Progress",
        }
    )

    assert operation.assigned_resource_id is None
    assert operation.status is OperationStatus.IN_PROGRESS


def test_resource_mapping_defaults_and_activity_flag():
    resource = row_to_resource({"id": "MCH-1", "name": "Mill", "is_active": False})

    assert resource.resource_type is ResourceType.MACHINE
    assert resource.is_active is False


def test_resource_mapping_treats_null_activity_as_active():
    resource = row_to_resource({"id": "MCH-2", "name": "Lathe", "is_active": None})

    assert resource.is_active is True


def test_material_mapping_converts_numeric_values():
    material = row_to_material(
        {
            "id": "MAT-1",
            "name": "Steel",
            "quantity_available": Decimal("12.50"),
            "available_date_minutes": 120,
        }
    )

    assert material.quantity_available == 12.5
    assert material.available_date_minutes == 120


def test_item_routing_and_junction_mappings():
    item = row_to_item({"id": "ITEM-1", "name": "Bracket", "sku": "BR-1"})
    template = row_to_routing_template(
        {
            "id": 7,
            "target_item_id": "ITEM-1",
            "step_sequence": 10,
            "required_resource_type": "Human",
            "standard_duration_minutes": 30,
        }
    )
    dependency = row_to_operation_dependency(
        {"upstream_op_id": "OP-1", "downstream_op_id": "OP-2"}
    )
    requirement = row_to_operation_material(
        {
            "operation_id": "OP-1",
            "material_id": "MAT-1",
            "quantity_required": Decimal("2.500"),
        }
    )

    assert item.sku == "BR-1"
    assert template.id == 7
    assert template.required_resource_type is ResourceType.HUMAN
    assert dependency.downstream_op_id == "OP-2"
    assert requirement.quantity_required == 2.5


def test_calendar_mappings():
    shift = row_to_factory_shift(
        {
            "id": 3,
            "resource_id": "MCH-1",
            "day_of_week": 1,
            "start_time": time(8, 0),
            "end_time": time(17, 0),
        }
    )
    holiday = row_to_factory_holiday(
        {"id": 4, "holiday_date": date(2026, 1, 1), "description": "New Year"}
    )

    assert shift.start_time == time(8, 0)
    assert shift.id == 3
    assert holiday.holiday_date == date(2026, 1, 1)
    assert holiday.description == "New Year"


def test_missing_required_field_raises_validation_error():
    with pytest.raises(ValidationError, match="target_item_id"):
        row_to_work_order({"id": "WO-1"})


def test_unknown_enum_value_raises_validation_error():
    with pytest.raises(ValidationError, match="OperationStatus"):
        row_to_operation(
            {
                "id": "OP-1",
                "work_order_id": "WO-1",
                "sequence_number": 10,
                "duration_minutes": 45,
                "assigned_resource_id": "MCH-1",
                "status": "Pending",
            }
        )
