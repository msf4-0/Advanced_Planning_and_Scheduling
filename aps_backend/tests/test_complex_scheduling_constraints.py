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

    @patch('classes.ScheduleCreator.Repository')
    @patch('classes.ScheduleCreator.ConnectionManager')
    @patch('classes.ScheduleCreator.DatabaseConfig')
    def test_parallel_dependencies_and_overlap_protection(self, mock_config, mock_conn_manager, mock_repo_class):
        """
        Validates:
        1. True Parallel Dependencies (Task B and C run simultaneously at minute 0).
        2. Schedule now, run later (Task A waits for delayed material delivery at minute 180).
        3. Machine Overlap Protection (Verifies isolated machines allow parallel tracks).
        """
        
        # --- CONDITION 2: SCHEDULE NOW, RUN LATER DATA CONFIG ---
        # Component parts arrive late at minute 180, pushing downstream Task A into the future
        mock_db_materials = [
            {"id": "LATE-PART-XYZ", "name": "Late Component", "quantity_available": 0.0, "available_date_minutes": 180}
        ]

        # Provide isolated machines to allow true parallel processing lanes
        mock_db_resources = [
            {"id": "WORKSTATION-ALPHA", "name": "Assembly Lane Alpha", "resource_type": "Machine", "is_active": True},
            {"id": "WORKSTATION-BETA", "name": "Assembly Lane Beta", "resource_type": "Machine", "is_active": True},
            {"id": "WORKSTATION-GAMMA", "name": "Assembly Lane Gamma", "resource_type": "Machine", "is_active": True}
        ]

        # --- CONDITION 1 & 3: MULTIPLE PARALLEL DEPENDENCIES CONFIG ---
        # Task B and Task C are independent of each other and on separate machines
        mock_db_operations = [
            {"id": "TASK-B", "work_order_id": "WO-002", "sequence_number": 1, "duration_minutes": 60, "assigned_resource_id": "WORKSTATION-ALPHA", "status": "Pending"},
            {"id": "TASK-C", "work_order_id": "WO-002", "sequence_number": 1, "duration_minutes": 45, "assigned_resource_id": "WORKSTATION-BETA", "status": "Pending"},
            {"id": "TASK-A", "work_order_id": "WO-002", "sequence_number": 2, "duration_minutes": 30, "assigned_resource_id": "WORKSTATION-GAMMA", "status": "Pending"}
        ]

        # TASK-A strictly requires both TASK-B AND TASK-C to complete first
        mock_db_dependencies = [
            {"upstream_op_id": "TASK-B", "downstream_op_id": "TASK-A"},
            {"upstream_op_id": "TASK-C", "downstream_op_id": "TASK-A"}
        ]

        # TASK-A also requires the late component material arrival (Condition 2)
        mock_db_material_requirements = [
            {"operation_id": "TASK-A", "material_id": "LATE-PART-XYZ", "quantity_required": 1.0}
        ]

        # --- CONFIGURE THE MOCK REPOSITORY FACTORY ---
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

        # --- EXECUTE THE SOLVER ENGINE PIPELINE ---
        summary_results = schedule_creator_run()

        # Extract calculated scheduling minutes output variables
        b_start = summary_results["TASK-B"]["start_minute"]
        b_end = summary_results["TASK-B"]["end_minute"]
        
        c_start = summary_results["TASK-C"]["start_minute"]
        c_end = summary_results["TASK-C"]["end_minute"]
        
        a_start = summary_results["TASK-A"]["start_minute"]

        # =====================================================================
        # ASSERTION CRITERIA 1 & 3: TRUE PARALLEL TIMELINES
        # =====================================================================
        # Because they have separate resources, both should launch immediately at minute 0
        self.assertEqual(b_start, 0, f"Parallel Failure: Task B delayed starting at minute {b_start}")
        self.assertEqual(c_start, 0, f"Parallel Failure: Task C delayed starting at minute {c_start}")
        
        # Verify execution overlaps completely (e.g., Task C runs entirely inside Task B's timeline window)
        self.assertTrue(c_end <= b_end, "Timeline Math Error: Parallel overlap assertion failed.")

        # =====================================================================
        # ASSERTION CRITERIA 2: MULTIPLE DEPENDENCIES & RUN LATER (Material Hold)
        # =====================================================================
        # Upstream tasks finish at minute 60, but Task A must wait until minute 180 for material arrivals
        self.assertTrue(
            a_start >= b_end, 
            f"Dependency Failure: Task A started at {a_start} before Upstream Task B finished at {b_end}"
        )
        self.assertTrue(
            a_start >= c_end, 
            f"Dependency Failure: Task A started at {a_start} before Upstream Task C finished at {c_end}"
        )
        self.assertTrue(
            a_start >= 180, 
            f"Material Lag Failure: Task A scheduled early at {a_start}, breaking the 'Run Later' constraint of minute 180"
        )

if __name__ == "__main__":
    unittest.main()
