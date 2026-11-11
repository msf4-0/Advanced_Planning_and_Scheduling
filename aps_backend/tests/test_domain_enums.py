"""Tests for shared domain enums and their database/API vocabulary."""

import json

from app.domain.enums import (
    OperationStatus,
    ResourceType,
    RunStatus,
    SolverStatus,
    WorkOrderStatus,
)


def test_operation_status_values_match_the_database_vocabulary():
    assert [status.value for status in OperationStatus] == [
        "Draft",
        "Scheduled",
        "In Progress",
        "Done",
    ]


def test_work_order_status_values_match_the_database_vocabulary():
    assert [status.value for status in WorkOrderStatus] == [
        "Draft",
        "Approved",
        "Scheduled",
        "In Progress",
        "Done",
    ]


def test_run_status_values_cover_the_worker_lifecycle():
    assert [status.value for status in RunStatus] == [
        "Queued",
        "Running",
        "Success",
        "Failed",
        "Cancelled",
    ]


def test_solver_status_values_match_or_tools_names():
    assert [status.value for status in SolverStatus] == [
        "UNKNOWN",
        "MODEL_INVALID",
        "FEASIBLE",
        "INFEASIBLE",
        "OPTIMAL",
    ]


def test_resource_types_match_the_schema_comments():
    assert [resource_type.value for resource_type in ResourceType] == [
        "Machine",
        "Human",
        "Tooling",
    ]


def test_string_enums_serialize_as_plain_strings():
    assert OperationStatus.DONE == "Done"
    assert isinstance(OperationStatus.DONE, str)
    assert str(OperationStatus.DONE) == "Done"
    assert json.dumps({"status": OperationStatus.DONE}) == '{"status": "Done"}'
