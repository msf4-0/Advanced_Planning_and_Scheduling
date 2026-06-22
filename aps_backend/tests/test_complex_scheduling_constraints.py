# tests/test_complex_scheduling_constraints.py
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Force path resolution base to the project root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the run module targeting its real file location inside classes/
from classes.ScheduleCreator import run as schedule_creator_run


class TestComplexParallelSchedulingConstraints(unittest.TestCase):

    def setUp(self):
        """Initializes reusable mock structures for clean, isolated test runs."""
        self.mock_config_patch = patch('classes.ScheduleCreator.DatabaseConfig')
        self.mock_conn_patch = patch('classes.ScheduleCreator.ConnectionManager')
        self.mock_repo_patch = patch('classes.ScheduleCreator.Repository')
        
        self.mock_config_patch.start()
        self.mock_conn_patch.start()
        self.mock_repo_class = self.mock_repo_patch.start()
        
    def tearDown(self):
        """Clean up active mock patches after each test execution."""
        patch.stopall()

    def _configure_mock_repository(self, resources=None, materials=None, operations=None, dependencies=None, material_reqs=None):
        """Helper to inject specific operational mock data shapes safely into the solver."""
        def mock_repo_side_effect(table_name, connection_manager=None):
            mock_repo = MagicMock()
            mock_repo.table_name = table_name
            
            mapping = {
                "resources": resources or [],
                "materials": materials or [],
                "operations": operations or [],
                "operation_dependencies": dependencies or [],
                "operation_materials": material_reqs or []
            }
            mock_repo.fetch_all.return_value = mapping.get(table_name, [])
            return mock_repo

        self.mock_repo_class.side_effect = mock_repo_side_effect


    # =====================================================================
    # TEST CASE 1: MACHINE OVERLAP PROTECTION & PARALLEL LANES
    # =====================================================================
    def test_isolated_machines_allow_true_parallel_execution(self):
        """Verifies independent tasks on separate machines launch simultaneously at minute 0."""
        mock_resources = [
            {"id": "MCH-ALPHA", "name": "Lane Alpha", "resource_type": "Machine", "is_active": True},
            {"id": "MCH-BETA", "name": "Lane Beta", "resource_type": "Machine", "is_active": True}
        ]
        mock_operations = [
            {"id": "TASK-B", "work_order_id": "WO-002", "sequence_number": 1, "duration_minutes": 60, "assigned_resource_id": "MCH-ALPHA", "status": "Pending"},
            {"id": "TASK-C", "work_order_id": "WO-002", "sequence_number": 1, "duration_minutes": 45, "assigned_resource_id": "MCH-BETA", "status": "Pending"}
        ]

        self._configure_mock_repository(resources=mock_resources, operations=mock_operations)
        summary = schedule_creator_run()

        # Both tasks must start immediately at minute 0
        self.assertEqual(summary["TASK-B"]["start_minute"], 0)
        self.assertEqual(summary["TASK-C"]["start_minute"], 0)


    # =====================================================================
    # TEST CASE 2: MULTIPLE PARALLEL DEPENDENCIES (THE JOIN/MERGE)
    # =====================================================================
    def test_downstream_task_waits_for_all_upstream_dependencies_to_complete(self):
        """Verifies a downstream task waits for the absolute latest completing parent task."""
        mock_resources = [
            {"id": "MCH-A", "resource_type": "Machine", "is_active": True},
            {"id": "MCH-B", "resource_type": "Machine", "is_active": True},
            {"id": "MCH-C", "resource_type": "Machine", "is_active": True}
        ]
        # Task B takes 60 min, Task C takes 45 min. Both run in parallel at minute 0.
        mock_operations = [
            {"id": "TASK-B", "work_order_id": "WO-002", "sequence_number": 1, "duration_minutes": 60, "assigned_resource_id": "MCH-A", "status": "Pending"},
            {"id": "TASK-C", "work_order_id": "WO-002", "sequence_number": 1, "duration_minutes": 45, "assigned_resource_id": "MCH-B", "status": "Pending"},
            {"id": "TASK-A", "work_order_id": "WO-002", "sequence_number": 2, "duration_minutes": 30, "assigned_resource_id": "MCH-C", "status": "Pending"}
        ]
        mock_dependencies = [
            {"upstream_op_id": "TASK-B", "downstream_op_id": "TASK-A"},
            {"upstream_op_id": "TASK-C", "downstream_op_id": "TASK-A"}
        ]

        self._configure_mock_repository(resources=mock_resources, operations=mock_operations, dependencies=mock_dependencies)
        summary = schedule_creator_run()

        # Task A should start immediately at minute 60 (exactly when the longer parent Task B finishes)
        self.assertEqual(summary["TASK-A"]["start_minute"], 60, "Task A should optimize tightly to minute 60.")


    # =====================================================================
    # TEST CASE 3: MATERIAL ARRIVAL LAGS (SCHEDULE NOW, RUN LATER)
    # =====================================================================
    def test_material_availability_date_forces_future_scheduling_hold(self):
        """Verifies that inventory arrival constraints correctly push optimization timelines out."""
        mock_resources = [
            {"id": "MCH-C", "resource_type": "Machine", "is_active": True}
        ]
        mock_operations = [
            {"id": "TASK-A", "work_order_id": "WO-002", "sequence_number": 1, "duration_minutes": 30, "assigned_resource_id": "MCH-C", "status": "Pending"}
        ]
        # Component parts arrive late at minute 180
        mock_materials = [
            {"id": "LATE-PART-XYZ", "name": "Late Component", "quantity_available": 0.0, "available_date_minutes": 180}
        ]
        mock_material_reqs = [
            {"operation_id": "TASK-A", "material_id": "LATE-PART-XYZ", "quantity_required": 1.0}
        ]

        self._configure_mock_repository(
            resources=mock_resources, 
            operations=mock_operations, 
            materials=mock_materials, 
            material_reqs=mock_material_reqs
        )
        summary = schedule_creator_run()

        # Task A has no parent tasks, but must hold until minute 180 for inventory
        self.assertEqual(summary["TASK-A"]["start_minute"], 180, "Task A failed to enforce the inventory lag date.")


if __name__ == "__main__":
    unittest.main()
