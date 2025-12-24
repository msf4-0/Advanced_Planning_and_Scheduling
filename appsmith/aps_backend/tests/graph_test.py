import pytest
from aps_backend.routes import RouteRepository, RouteService
from appsmith.aps_backend.api_models import OpStepCreate, RouteFilter
from appsmith.aps_backend.db.connection import get_connection

@pytest.fixture
def db_conn():
    conn = get_connection()
    yield conn
    conn.close()

@pytest.fixture
def repo(db_conn):
    return RouteRepository(db_conn)

@pytest.fixture
def service(repo):
    return RouteService(repo)

def test_add_and_validate_step(service):
    product_id = 1001
    operation_id = 2001

    # Clean up before test
    try:
        steps = service.repo.get_steps_for_product(product_id)
        for s in steps:
            service.delete_step(product_id, s.sequence)
    except Exception:
        pass

    # Add a step
    service.add_step_to_route(product_id, operation_id)
    route = service.get_product_route(product_id)
    assert len(route.steps) == 1
    assert route.steps[0].operation.operation_id == operation_id

    # Validate route
    assert service.validate_route(product_id)

def test_insert_step_in_middle(service):
    product_id = 1002
    op_ids = [201, 202, 203]

    # Clean up before test
    try:
        steps = service.repo.get_steps_for_product(product_id)
        for s in steps:
            service.delete_step(product_id, s.sequence)
    except Exception:
        pass

    # Add two steps
    service.add_step_to_route(product_id, op_ids[0])
    service.add_step_to_route(product_id, op_ids[2])
    # Insert in the middle
    service.add_step_to_route(product_id, op_ids[1], insert_after=1)
    route = service.get_product_route(product_id)
    assert [s.operation.operation_id for s in route.steps] == op_ids

def test_delete_step(service):
    product_id = 1003
    op_ids = [301, 302, 303]

    # Clean up before test
    try:
        steps = service.repo.get_steps_for_product(product_id)
        for s in steps:
            service.delete_step(product_id, s.sequence)
    except Exception:
        pass

    # Add steps
    for op_id in op_ids:
        service.add_step_to_route(product_id, op_id)
    # Delete the middle step
    service.delete_step(product_id, 2)
    route = service.get_product_route(product_id)
    assert [s.operation.operation_id for s in route.steps] == [301, 303]
    assert [s.sequence for s in route.steps] == [1, 2]

def test_reorder_steps(service):
    product_id = 1004
    op_ids = [401, 402, 403]

    # Clean up before test
    try:
        steps = service.repo.get_steps_for_product(product_id)
        for s in steps:
            service.delete_step(product_id, s.sequence)
    except Exception:
        pass

    # Add steps
    for op_id in op_ids:
        service.add_step_to_route(product_id, op_id)
    # Reorder
    new_order = [403, 401, 402]
    service.reorder_steps(product_id, new_order)
    route = service.get_product_route(product_id)
    assert [s.operation.operation_id for s in route.steps] == new_order
    assert [s.sequence for s in route.steps] == [1, 2, 3]