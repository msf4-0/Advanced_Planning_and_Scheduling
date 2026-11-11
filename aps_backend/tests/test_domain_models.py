"""Smoke tests for the domain dataclasses."""

from datetime import date, datetime, time

from app.domain import (
    FactoryHoliday,
    FactoryShift,
    Item,
    Material,
    Operation,
    OperationDependency,
    OperationMaterial,
    OperationStatus,
    Resource,
    ResourceType,
    RoutingTemplate,
    WorkOrder,
    WorkOrderStatus,
)


def test_domain_entities_construct_with_defaults():
    work_order = WorkOrder(
        id="WO-1",
        target_item_id="ITEM-1",
        quantity_to_make=10,
        due_date=datetime(2026, 1, 1, 8, 0),
    )
    assert work_order.status == WorkOrderStatus.DRAFT

    operation = Operation(
        id="OP-1",
        work_order_id="WO-1",
        sequence_number=10,
        duration_minutes=45,
    )
    assert operation.assigned_resource_id is None
    assert operation.status == OperationStatus.DRAFT

    resource = Resource(id="MCH-1", name="Mill")
    assert resource.resource_type == ResourceType.MACHINE
    assert resource.is_active is True

    material = Material(id="MAT-1", name="Steel")
    assert material.quantity_available == 0.0
    assert material.available_date_minutes == 0

    assert Item(id="ITEM-1", name="Bracket", sku="BR-1").sku == "BR-1"

    template = RoutingTemplate(
        target_item_id="ITEM-1",
        step_sequence=10,
        required_resource_type=ResourceType.MACHINE,
        standard_duration_minutes=30,
    )
    assert template.id is None

    dependency = OperationDependency(
        upstream_op_id="OP-1",
        downstream_op_id="OP-2",
    )
    assert dependency.downstream_op_id == "OP-2"

    requirement = OperationMaterial(
        operation_id="OP-1",
        material_id="MAT-1",
        quantity_required=2.5,
    )
    assert requirement.quantity_required == 2.5

    shift = FactoryShift(
        resource_id="MCH-1",
        day_of_week=1,
        start_time=time(8, 0),
        end_time=time(17, 0),
    )
    assert shift.id is None

    holiday = FactoryHoliday(holiday_date=date(2026, 1, 1))
    assert holiday.description is None
    assert holiday.id is None
