# tests/test_complex_scheduling_constraints.py
import os
import sys
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

# Force path resolution base to the project root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the run module targeting its real file location inside classes/
from classes.ScheduleCreator import run as schedule_creator_run

class TestComplexSchedulingConstraints(unittest.TestCase):

    @patch('classes.ScheduleCreator.Repository')
    @patch('classes.ScheduleCreator.ConnectionManager')
    @patch('classes.ScheduleCreator.DatabaseConfig')
    def test_complex_scheduling_rules(self, mock_config, mock_conn_manager, mock_repo_class):
        """
        Validates:
        1. Multiple dependencies (Task A waits for both Task B and Task C).
        2. Schedule now, run later (Operations respect future material/earliest start constraints).
        3. Resource machine containment (Tasks on the same machine do not overlap).
        """
        
        # --- CONDITION 2: SCHEDULE NOW, RUN LATER DATA CONFIG ---
        # Component parts arrive late at minute 180, pushing downstream tasks deep into the future
        mock_db_materials = [
            {"id": "LATE-PART-XYZ", "name": "Late Component", "quantity_available": 0.0, "available_date_minutes": 180}
        ]

        # Shared single machine asset to thoroughly validate overlap safety constraints
        mock_db_resources = [
            {"id": "WORKSTATION-1", "name": "Assembly Workstation 1", "resource_type": "Machine", "is_active": True}
        ]

        # --- CONDITION 1 & 3: MULTIPLE DEPENDENCIES & NO OVERLAPS CONFIG ---
        # Task A will be downstream. Task B and Task C run early but share WORKSTATION-1.
        mock_db_operations = [
            {"id": "TASK-B", "work_order_id": "WO-002", "sequence_number": 1, "duration_minutes": 60, "assigned_resource_id": "WORKSTATION-1", "status": "Pending"},
            {"id": "TASK-C", "work_order_id": "WO-002", "sequence_number": 1, "duration_minutes": 45, "assigned_resource_id": "WORKSTATION-1", "status": "Pending"},
            {"id": "TASK-A", "work_order_id": "WO-002", "sequence_number": 2, "duration_minutes": 30, "assigned_resource_id": "WORKSTATION-1", "status": "Pending"}
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
        # ASSERTION CRITERIA 1: MULTIPLE DEPENDENCIES (Task A waits for B and C)
        # =====================================================================
        self.assertTrue(
            a_start >= b_end, 
            f"Dependency Failure: Task A started at {a_start} before Upstream Task B finished at {b_end}"
        )
        self.assertTrue(
            a_start >= c_end, 
            f"Dependency Failure: Task A started at {a_start} before Upstream Task C finished at {c_end}"
        )

        # =====================================================================
        # ASSERTION CRITERIA 2: SCHEDULE NOW, RUN LATER
        # =====================================================================
        # Even if upstream tasks finish early, Task A must wait until minute 180 for material arrivals
        self.assertTrue(
            a_start >= 180, 
            f"Material Lag Failure: Task A scheduled at {a_start}, breaking the 'Run Later' constraint of minute 180"
        )

        # =====================================================================
        # ASSERTION CRITERIA 3: MACHINE CAPACITY & OVERLAP PROTECTION
        # =====================================================================
        # Task B and Task C both run on WORKSTATION-1. They cannot overlap timelines.
        if b_start < c_start:
            # If B runs first, it must completely finish before C can begin
            self.assertTrue(c_start >= b_end, f"Overlap Error: Task C started at {c_start} before Task B cleared at {b_end}")
        else:
            # If C runs first, it must completely finish before B can begin
            self.assertTrue(b_start >= c_end, f"Overlap Error: Task B started at {b_start} before Task C cleared at {c_end}")

        # Ensure all tasks kept their static duration assignments intact during resolution shifts
        self.assertEqual(b_end - b_start, 60, "Data Mutation Error: Task B duration distorted by solver!")
        self.assertEqual(c_end - c_start, 45, "Data Mutation Error: Task C duration distorted by solver!")

if __name__ == "__main__":
    unittest.main()
