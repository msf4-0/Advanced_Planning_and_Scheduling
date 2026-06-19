# tests/test_schedule_creator.py
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Force path resolution base to the project root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# FIX: Import the run module targeting its real file location inside classes/
from classes.ScheduleCreator import run as schedule_creator_run

class TestScheduleCreatorPipeline(unittest.TestCase):

    # FIX: Update patch targets to match the absolute module path used by python
    @patch('classes.ScheduleCreator.Repository')
    @patch('classes.ScheduleCreator.ConnectionManager')
    @patch('classes.ScheduleCreator.DatabaseConfig')
    def test_end_to_end_graph_builder_and_solver_with_erpnext_data(self, mock_config, mock_conn_manager, mock_repo_class):
        """
        Validates the ScheduleCreator graph mapping, constraint engine execution,
        and data update payload generation using realistic ERPNext database columns.
        """
        
        # 1. SETUP REALISTIC ERPNEXT DATA ROWS (As translated by Node-RED)
        mock_db_resources = [
            {"id": "Cutting Station Alpha", "name": "CNC Cutting Station Alpha", "resource_type": "Machine", "is_active": True},
            {"id": "Assembly Line Beta", "name": "Manual Assembly Line Beta", "resource_type": "Machine", "is_active": True}
        ]

        mock_db_materials = [
            {"id": "RAW-STL-BAR-10MM", "name": "Stainless Steel Bar 10mm", "quantity_available": 250.0, "available_date_minutes": 0},
            {"id": "COMP-CTRL-BOARD-V2", "name": "Control Board Assembly V2", "quantity_available": 0.0, "available_date_minutes": 120}
        ]

        mock_db_operations = [
            {"id": "row_hash_op101", "work_order_id": "MFG-WO-2026-00001", "sequence_number": 1, "duration_minutes": 45, "assigned_resource_id": "Cutting Station Alpha", "status": "Pending"},
            {"id": "row_hash_op102", "work_order_id": "MFG-WO-2026-00001", "sequence_number": 2, "duration_minutes": 30, "assigned_resource_id": "Cutting Station Alpha", "status": "Pending"},
            {"id": "row_hash_op103", "work_order_id": "MFG-WO-2026-00001", "sequence_number": 3, "duration_minutes": 60, "assigned_resource_id": "Assembly Line Beta", "status": "Pending"}
        ]

        mock_db_dependencies = [
            {"upstream_op_id": "row_hash_op101", "downstream_op_id": "row_hash_op102"},
            {"upstream_op_id": "row_hash_op102", "downstream_op_id": "row_hash_op103"}
        ]

        mock_db_material_requirements = [
            {"operation_id": "row_hash_op101", "material_id": "RAW-STL-BAR-10MM", "quantity_required": 2.5},
            {"operation_id": "row_hash_op103", "material_id": "COMP-CTRL-BOARD-V2", "quantity_required": 1.0}
        ]

        # 2. CONFIGURE THE MOCK REPOSITORY INSTANCES
        repo_instances = {}
        
        def mock_repo_side_effect(table_name, connection_manager=None):
            mock_repo = MagicMock()
            mock_repo.table_name = table_name
            
            if table_name == "resources":
                mock_repo.fetch_all.return_value = mock_db_resources
            elif table_name == "materials":
                mock_repo.fetch_all.return_value = mock_db_materials
            elif table_name == "operations":
                mock_repo.fetch_all.return_value = mock_db_operations
            elif table_name == "operation_dependencies":
                mock_repo.fetch_all.return_value = mock_db_dependencies
            elif table_name == "operation_materials":
                mock_repo.fetch_all.return_value = mock_db_material_requirements
            else:
                mock_repo.fetch_all.return_value = []
                
            repo_instances[table_name] = mock_repo
            return mock_repo

        mock_repo_class.side_effect = mock_repo_side_effect

        # 3. TRIGGER THE PIPELINE WORKFLOW UNDER TEST
        # Calls the function imported from classes.ScheduleCreator
        summary_results = schedule_creator_run()

        # 4. MATHEMATICAL AND STRUCTURAL ASSERTIONS
        self.assertIsNotNone(summary_results, "Pipeline failed: Output summary dictionary is empty!")
        self.assertIn("row_hash_op101", summary_results)
        self.assertIn("row_hash_op102", summary_results)
        self.assertIn("row_hash_op103", summary_results)

        op101_end = summary_results["row_hash_op101"]["end_minute"]
        op102_start = summary_results["row_hash_op102"]["start_minute"]
        op102_end = summary_results["row_hash_op102"]["end_minute"]
        op103_start = summary_results["row_hash_op103"]["start_minute"]

        # Test Sequential Constraint
        self.assertTrue(op102_start >= op101_end, "Constraint Error: Sequential dependency layout was broken!")

        # Test Material Constraint
        self.assertTrue(op103_start >= 120, "Constraint Error: Operation started before its raw material arrival timeline!")

        # 5. VERIFY INTERACTION AND DATA WRITEBACK PAYLOADS
        op_repo_mock = repo_instances["operations"]
        op_repo_mock.batch_update.assert_called_once()
        
        called_args, called_kwargs = op_repo_mock.batch_update.call_args
        passed_batch = called_args[0] if called_args else called_kwargs["records"]
        
        for update_record in passed_batch:
            self.assertIn(update_record["id"], ["row_hash_op101", "row_hash_op102", "row_hash_op103"])
            self.assertIn("optimized_start_minute", update_record)
            self.assertIn("optimized_end_minute", update_record)
            self.assertIn("scheduled_start_time", update_record)
            self.assertIn("scheduled_end_time", update_record)
            self.assertEqual(update_record["status"], "Scheduled")

        # Verify tracking runs entry
        runs_repo_mock = repo_instances["scheduling_runs"]
        runs_repo_mock.add.assert_called_once()
        
        add_args, add_kwargs = runs_repo_mock.add.call_args
        log_payload = add_args[0] if add_args else add_kwargs["data"]
        
        self.assertEqual(log_payload["run_status"], "Success")

if __name__ == "__main__":
    unittest.main()
