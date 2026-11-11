"""Golden regression test for the current scheduling engine.

This test intentionally runs without a database and without Docker. It builds a
small in-memory graph, solves it with a fixed seed and a single search worker,
and compares the result to a checked-in fixture. The Phase 3 solver refactor
must keep this behavior unchanged under the default policy.
"""

import json
from pathlib import Path

from classes import APSEngine, ProcessNode, ResourceNode, SupplyNode

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "golden_schedule.json"


def load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def build_graph(spec: dict):
    resources = {
        resource["id"]: ResourceNode(
            resource_id=resource["id"],
            resource_type=resource.get("resource_type", "Machine"),
        )
        for resource in spec["resources"]
    }

    materials = {
        material["id"]: SupplyNode(
            materialId=material["id"],
            name=material["name"],
            quantityAvailable=material["quantity_available"],
            available_date=material["available_date"],
        )
        for material in spec["materials"]
    }

    operations = {}
    for operation_spec in spec["operations"]:
        operation = ProcessNode(
            operation_id=operation_spec["id"],
            duration=operation_spec["duration"],
            job_id=operation_spec["job_id"],
        )
        operation.add_compatible_resource(resources[operation_spec["resource_id"]])
        for material_id in operation_spec["material_ids"]:
            operation.add_input_material(materials[material_id])
        operations[operation.id] = operation

    for dependency in spec["dependencies"]:
        operations[dependency["upstream"]].add_next_operation(
            operations[dependency["downstream"]]
        )

    return operations, resources


def solve(spec: dict):
    operations, resources = build_graph(spec)

    engine = APSEngine(horizon_days=spec["horizon_days"])
    # Determinism: the production defaults (60s, 4 workers) may explore different
    # optimal solutions, so the regression test pins the search configuration.
    engine.solver.parameters.num_search_workers = 1
    engine.solver.parameters.random_seed = 0

    status = engine.build_and_solve(
        list(operations.values()), list(resources.values())
    )
    assignments = {
        operation_id: {
            "start": operation.optimized_start,
            "end": operation.optimized_end,
        }
        for operation_id, operation in operations.items()
    }
    return status, assignments


def test_golden_schedule_matches_fixture():
    spec = load_fixture()
    status, assignments = solve(spec)

    assert status == spec["expected"]["status"]
    assert assignments == spec["expected"]["assignments"]
    assert max(item["end"] for item in assignments.values()) == spec["expected"]["makespan"]


def test_golden_schedule_is_deterministic():
    spec = load_fixture()

    assert solve(spec) == solve(spec)
