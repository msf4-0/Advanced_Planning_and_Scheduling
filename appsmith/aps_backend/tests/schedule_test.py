import pytest
from unittest.mock import MagicMock, patch
from service import OpStepService, Schedule
from repository import GraphEditor, DBTable

@pytest.fixture
def mock_db():
    db = MagicMock(spec=DBTable)
    db.fetch_machines.return_value = [
        {'type': 'CNC', 'name': 'CNC-1'},
        {'type': 'CNC', 'name': 'CNC-2'},
        {'type': 'Drill', 'name': 'Drill-1'}
    ]
    db.get_connection.return_value = MagicMock()
    return db

@pytest.fixture
def mock_graph_editor():
    editor = MagicMock(spec=GraphEditor)
    editor.get_edges.return_value = []
    editor.get_node.side_effect = lambda node_type, query: []
    return editor

@pytest.fixture
def mock_opstep_service():
    service = MagicMock(spec=OpStepService)
    service.get_ready_opsteps.return_value = []
    return service

@pytest.fixture
def schedule_instance(mock_db, mock_graph_editor, mock_opstep_service):
    with patch('service.scheduler.DBTable', return_value=mock_db), \
        patch('service.scheduler.GraphEditor', return_value=mock_graph_editor), \
        patch('service.OpStepService', return_value=mock_opstep_service):
        sched = Schedule()
        sched.db = mock_db
        sched.graph_editor = mock_graph_editor
        sched.service = mock_opstep_service
        return sched

def test_init_machines(schedule_instance):
    machines = schedule_instance.get_machines()
    assert 'CNC' in machines
    assert 'Drill' in machines
    assert machines['CNC'] == ['CNC-1', 'CNC-2']
    assert machines['Drill'] == ['Drill-1']

def test_reset(schedule_instance):
    schedule_instance.completed_schedule = [1, 2, 3]
    schedule_instance.current_time = 10
    schedule_instance.machines = {'A': ['A1']}
    schedule_instance.reset()
    assert schedule_instance.completed_schedule == []
    assert schedule_instance.machines == {}
    assert schedule_instance.current_time == 0

def test_get_final_schedule(schedule_instance):
    schedule_instance.completed_schedule = [{'order_id': 1}]
    assert schedule_instance.get_final_schedule() == [{'order_id': 1}]

def test_get_gantt_friendly_schedule(schedule_instance):
    schedule_instance.completed_schedule = [
        {'order_id': 1, 'start_time': 0, 'duration': 10, 'assigned_machine': 'CNC-1', 'machine_type': 'CNC'},
        {'order_id': 2, 'start_time': 5, 'duration': 15, 'assigned_machine': 'Drill-1', 'machine_type': 'Drill'}
    ]
    result = schedule_instance.get_gantt_friendly_schedule()
    assert result[0]['Task'] == 'Order 1'
    assert result[0]['Start'] == 0
    assert result[0]['Finish'] == 10
    assert result[0]['Resource'] == 'CNC-1'
    assert result[1]['Resource'] == 'Drill-1'

def test_machine_assigner_assigns_machines(schedule_instance):
    schedule_instance.machines = {'CNC': ['CNC-1', 'CNC-2']}
    schedule_instance.completed_schedule = [
        {'order_id': 1, 'machine_type': 'CNC', 'start_time': 0, 'duration': 5},
        {'order_id': 2, 'machine_type': 'CNC', 'start_time': 2, 'duration': 5},
        {'order_id': 3, 'machine_type': 'CNC', 'start_time': 6, 'duration': 5}
    ]
    schedule_instance.machine_assigner()
    assigned = [step['assigned_machine'] for step in schedule_instance.completed_schedule]
    assert set(assigned).issubset({'CNC-1', 'CNC-2'})

def test_create_schedule_no_ready_steps(schedule_instance):
    schedule_instance.service.get_ready_opsteps.return_value = []
    schedule_instance.current_time = 0
    schedule_instance.create_schedule(max_horizon=2)
    assert schedule_instance.current_time == 2

def test_create_schedule_with_ready_steps(schedule_instance, mock_graph_editor):
    # Setup ready steps and mock graph editor
    class DummyOp:
        duration = 3
        machine_type = 'CNC'
        material_id = 1
    class DummyStep:
        order_id = 1
        sequence = 101
        operation = DummyOp()
    schedule_instance.service.get_ready_opsteps.return_value = [DummyStep()]
    mock_graph_editor.get_edges.return_value = []
    mock_graph_editor.get_node.side_effect = lambda node_type, query: []
    mock_graph_editor.update_node.return_value = None
    schedule_instance.machines = {'CNC': ['CNC-1', 'CNC-2']}
    schedule_instance.current_time = 0
    schedule_instance.create_schedule(max_horizon=5)
    assert any(s['order_id'] == 1 for s in schedule_instance.completed_schedule)