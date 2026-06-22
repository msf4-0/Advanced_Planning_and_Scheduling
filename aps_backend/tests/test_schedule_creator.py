# tests/test_schedule_creator.py
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Force path resolution base to the project root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the run module targeting its real file location inside classes/
from classes.ScheduleCreator import run as schedule_creator_run


class TestScheduleCreatorPipeline(unittest.TestCase):

    def setUp(self):
        """Initializes reusable mock patches for clean, isolated test states."""
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
        """Helper to inject isolated data tables into the repository factory."""
        repo_instances = {}
        
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
            repo_instances[table_name] = mock_repo
            return mock_repo

        self.mock_repo_class.side_effect = mock_repo_side_effect
        return repo_instances


    # =====================================================================
    # TEST CASE 1: SEQUENTIAL ERPNEXT GRAPH CONSTRAINTS
    # =====================================================================
    def test_erpnext_sequential_dependency_execution(self):
        """Verifies that subsequent tasks execute only after their upstream parents finish."""
        mock_resources = [
            {"id": "Cutting Station Alpha", "name": "CNC Cutting Station Alpha", "resource_type": "Machine", "is_active": True}
        ]
        mock_operations = [
            {"id": "row_hash_op101", "work_order_id": "MFG-WO-2026-00001", "sequence_number": 1, "duration_minutes": 45, "assigned_resource_id": "Cutting Station Alpha", "status": "Pending"},
            {"id": "row_hash_op102", "work_order_id": "MFG-WO-2026-00001", "sequence_number": 2, "duration_minutes": 30, "assigned_resource_id": "Cutting Station Alpha", "status": "Pending"}
        ]
        mock_dependencies = [
            {"upstream_op_id": "row_hash_op101", "downstream_op_id": "row_hash_op102"}
        ]

        self._configure_mock_repository(resources=mock_resources, operations=mock_operations, dependencies=mock_dependencies)
        summary = schedule_creator_run()

        # Op 102 must start precisely at minute 45 when Op 101 finishes
        self.assertEqual(summary["row_hash_op101"]["start_minute"], 0)
        self.assertEqual(summary["row_hash_op101"]["end_minute"], 45)
        self.assertEqual(summary["row_hash_op102"]["start_minute"], 45)


    # =====================================================================
    # TEST CASE 2: ERPNEXT MATERIAL CONSTRAINT ENFORCEMENT
    # =====================================================================
    def test_erpnext_material_availability_hold(self):
        """Verifies that an operation is held back if its raw materials arrive late."""
        mock_resources = [
            {"id": "Assembly Line Beta", "name": "Manual Assembly Line Beta", "resource_type": "Machine", "is_active": True}
        ]
        mock_operations = [
            {"id": "row_hash_op103", "work_order_id": "MFG-WO-2026-00001", "sequence_number": 1, "duration_minutes": 60, "assigned_resource_id": "Assembly Line Beta", "status": "Pending"}
        ]
        mock_materials = [
            {"id": "COMP-CTRL-BOARD-V2", "name": "Control Board Assembly V2", "quantity_available": 0.0, "available_date_minutes": 120}
        ]
        mock_material_reqs = [
            {"operation_id": "row_hash_op103", "material_id": "COMP-CTRL-BOARD-V2", "quantity_required": 1.0}
        ]

        self._configure_mock_repository(
            resources=mock_resources, 
            operations=mock_operations, 
            materials=mock_materials, 
            material_reqs=mock_material_reqs
        )
        summary = schedule_creator_run()

        # Task must wait until minute 120 for material delivery
        self.assertEqual(summary["row_hash_op103"]["start_minute"], 120)


    # =====================================================================
    # TEST CASE 3: WRITEBACK DATA STRUCTURE & STATUS VERIFICATION
    # =====================================================================
    def test_database_writeback_payload_structure(self):
        """Verifies that the correct dictionary keys are packaged and batch-updated to the database."""
        mock_resources = [{"id": "Cutting Station Alpha", "resource_type": "Machine", "is_active": True}]
        mock_operations = [{"id": "row_hash_op101", "work_order_id": "MFG-WO-2026-00001", "sequence_number": 1, "duration_minutes": 45, "assigned_resource_id": "Cutting Station Alpha", "status": "Pending"}]

        repos = self._configure_mock_repository(resources=mock_resources, operations=mock_operations)
        schedule_creator_run()

        # Assert that operations batch update occurred
        op_repo_mock = repos["operations"]
        op_repo_mock.batch_update.assert_called_once()

        # Extract the updates list from called args/kwargs
        called_args, called_kwargs = op_repo_mock.batch_update.call_args
        passed_batch = called_args[0] if called_args else called_kwargs.get("updates", called_kwargs.get("records", []))

        # Validate updating dictionary fields
        for record in passed_batch:
            self.assertEqual(record["id"], "row_hash_op101")
            self.assertIn("optimized_start_minute", record)
            self.assertIn("optimized_end_minute", record)
            self.assertIn("scheduled_start_time", record)
            self.assertIn("scheduled_end_time", record)
            self.assertEqual(record["status"], "Scheduled")


    # =====================================================================
    # TEST CASE 4: SCHEDULING RUN TRACKING LOG ENTRY
    # =====================================================================
    def test_scheduling_run_initialization_log(self):
        """Verifies that the engine logs the workflow run execution with valid tracking statuses."""
        mock_resources = [{"id": "Cutting Station Alpha", "resource_type": "Machine", "is_active": True}]
        mock_operations = [{"id": "row_hash_op101", "work_order_id": "MFG-WO-2026-00001", "sequence_number": 1, "duration_minutes": 45, "assigned_resource_id": "Cutting Station Alpha", "status": "Pending"}]

        repos = self._configure_mock_repository(resources=mock_resources, operations=mock_operations)
        schedule_creator_run()

        # Assert that scheduling track entry was created
        runs_repo_mock = repos["scheduling_runs"]
        runs_repo_mock.add.assert_called_once()

        called_args, called_kwargs = runs_repo_mock.add.call_args
        log_payload = called_args[0] if called_args else called_kwargs.get("data", called_kwargs)

        # Confirm the payload supports the runtime lifecycle states
        self.assertIn(log_payload["run_status"], ["Success", "Running"])


if __name__ == "__main__":
    unittest.main()
