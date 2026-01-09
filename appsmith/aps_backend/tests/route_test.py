import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from service import ProductBlueprintService
from appsmith.aps_backend.api.blueprint_api import router

client = TestClient(router)

@pytest.fixture
def mock_graph():
    return MagicMock()

@pytest.fixture
def route_service(mock_graph):
    return ProductBlueprintService(mock_graph)

def test_get_product_sequence_basic(route_service, mock_graph):
    mock_graph.get_node.return_value = [
        {'id': 1, 'product_id': 10, 'operation_id': 100, 'sequence': 1},
        {'id': 2, 'product_id': 10, 'operation_id': 101, 'sequence': 2},
    ]
    with patch('service.route_service.ProductRouteRead') as MockPRR, \
         patch('service.route_service.OpStepRead') as MockOSR:
        MockOSR.side_effect = lambda **kwargs: kwargs
        MockPRR.return_value = "route"
        result = route_service.get_product_sequence(10)
        assert result == "route"
        mock_graph.get_node.assert_called_with('OpStep', {'product_id': 10})

def test_validate_sequence_continuous(route_service):
    route_service.get_product_sequence = MagicMock()
    route_service.get_product_sequence.return_value = MagicMock(
        steps=[MagicMock(sequence=1), MagicMock(sequence=2), MagicMock(sequence=3)]
    )
    assert route_service.validate_sequence(1) is True

def test_validate_sequence_non_continuous(route_service):
    route_service.get_product_sequence = MagicMock()
    route_service.get_product_sequence.return_value = MagicMock(
        steps=[MagicMock(sequence=1), MagicMock(sequence=3)]
    )
    with pytest.raises(Exception):
        route_service.validate_sequence(1)

def test_add_opstep_appends(route_service, mock_graph):
    mock_graph.get_node.return_value = [
        {'id': 1, 'product_id': 10, 'operation_id': 100, 'sequence': 1}
    ]
    mock_graph.create_node.return_value = {'id': 2}
    route_service.rebuild_next_operation_edges = MagicMock()
    route_service.validate_sequence = MagicMock()
    route_service.add_opstep(10, 101)
    mock_graph.create_node.assert_called()
    route_service.rebuild_next_operation_edges.assert_called_with(10)
    route_service.validate_sequence.assert_called_with(10)

def test_delete_opstep_success(route_service, mock_graph):
    mock_graph.get_node.return_value = [{'id': 1, 'sequence': 1}]
    mock_graph.delete_node.return_value = None
    route_service.rebuild_next_operation_edges = MagicMock()
    route_service.validate_sequence = MagicMock()
    route_service.delete_opstep(10, 1)
    mock_graph.delete_node.assert_called()

def test_reorder_opsteps_success(route_service, mock_graph):
    mock_graph.get_node.return_value = [
        {'id': 1, 'operation_id': 100, 'sequence': 1},
        {'id': 2, 'operation_id': 101, 'sequence': 2}
    ]
    route_service.rebuild_next_operation_edges = MagicMock()
    route_service.validate_sequence = MagicMock()
    route_service.reorder_opsteps(10, [101, 100])
    route_service.rebuild_next_operation_edges.assert_called_with(10)
    route_service.validate_sequence.assert_called_with(10)

def test_reorder_opsteps_invalid(route_service, mock_graph):
    mock_graph.get_node.return_value = [
        {'id': 1, 'operation_id': 100, 'sequence': 1},
        {'id': 2, 'operation_id': 101, 'sequence': 2}
    ]
    with pytest.raises(Exception):
        route_service.reorder_opsteps(10, [999, 100])

# --- API TESTS ---

@patch("api.routes_api.get_service")
def test_api_get_route(mock_get_service):
    mock_service = MagicMock()
    mock_service.get_product_sequence.return_value = {"product_id": 1, "steps": []}
    mock_get_service.return_value = mock_service
    response = client.get("/products/1/route")
    assert response.status_code == 200
    assert response.json()["product_id"] == 1

@patch("api.routes_api.get_service")
def test_api_validate_route(mock_get_service):
    mock_service = MagicMock()
    mock_get_service.return_value = mock_service
    response = client.post("/products/1/route/validate", json={})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@patch("api.routes_api.get_service")
def test_api_add_step(mock_get_service):
    mock_service = MagicMock()
    mock_get_service.return_value = mock_service
    payload = {"operation_id": 101, "insert_after": None}
    response = client.post("/products/1/steps", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "step added"


if __name__ == "__main__":
    pytest.main()