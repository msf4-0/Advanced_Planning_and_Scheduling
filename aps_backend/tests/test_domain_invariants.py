"""Invariant and immutability tests for domain entities."""

from dataclasses import FrozenInstanceError
from datetime import datetime, time

import pytest

from app.domain import (
    FactoryShift,
    Material,
    Operation,
    OperationMaterial,
    RoutingTemplate,
    WorkOrder,
)
from app.domain.errors import ValidationError
from app.domain.enums import ResourceType, WorkOrderStatus


def _work_order(**overrides):
    values = {
        "id": "WO-1",
        "target_item_id": "ITEM-1",
        "quantity_to_make": 10,
        "due_date": datetime(2026, 1, 1, 8, 0),
    }
    values.update(overrides)
    return WorkOrder(**values)


def test_work_order_rejects_non_positive_quantity():
    with pytest.raises(ValidationError, match="quantity_to_make"):
        _work_order(quantity_to_make=0)


def test_operation_rejects_non_positive_duration():
    with pytest.raises(ValidationError, match="duration_minutes"):
        Operation(
            id="OP-1",
            work_order_id="WO-1",
            sequence_number=10,
            duration_minutes=0,
        )


def test_material_rejects_negative_stock_and_availability():
    with pytest.raises(ValidationError, match="quantity_available"):
        Material(id="MAT-1", name="Steel", quantity_available=-1)
    with pytest.raises(ValidationError, match="available_date_minutes"):
        Material(id="MAT-1", name="Steel", available_date_minutes=-1)


def test_operation_material_rejects_non_positive_requirement():
    with pytest.raises(ValidationError, match="quantity_required"):
        OperationMaterial(
            operation_id="OP-1",
            material_id="MAT-1",
            quantity_required=0,
        )


def test_routing_template_rejects_non_positive_values():
    with pytest.raises(ValidationError, match="step_sequence"):
        RoutingTemplate(
            target_item_id="ITEM-1",
            step_sequence=0,
            required_resource_type=ResourceType.MACHINE,
            standard_duration_minutes=30,
        )
    with pytest.raises(ValidationError, match="standard_duration_minutes"):
        RoutingTemplate(
            target_item_id="ITEM-1",
            step_sequence=10,
            required_resource_type=ResourceType.MACHINE,
            standard_duration_minutes=0,
        )


def test_factory_shift_rejects_invalid_day_and_time_range():
    with pytest.raises(ValidationError, match="day_of_week"):
        FactoryShift(
            resource_id="MCH-1",
            day_of_week=0,
            start_time=time(8, 0),
            end_time=time(17, 0),
        )
    with pytest.raises(ValidationError, match="start_time"):
        FactoryShift(
            resource_id="MCH-1",
            day_of_week=1,
            start_time=time(17, 0),
            end_time=time(8, 0),
        )


def test_domain_entities_are_immutable():
    work_order = _work_order()

    with pytest.raises(FrozenInstanceError):
        work_order.status = WorkOrderStatus.APPROVED
