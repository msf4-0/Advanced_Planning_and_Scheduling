import pytest
from unittest.mock import patch, MagicMock, call

# Import the main function
import app

@patch("app.DBTable")
@patch("app.DataIngestion")
@patch("app.Scheduler")
def test_main_successful_schedule(
    mock_scheduler_class,
    mock_data_ingestion_class,
    mock_dbtable_class,
    capsys
):
    """
    Test that main() runs successfully and prints schedule results
    """

    # ---- Mock DB connection ----
    mock_conn = MagicMock()
    mock_dbtable_class.return_value.get_connection.return_value = mock_conn

    # ---- Mock extracted data ----
    mock_ingestion = mock_data_ingestion_class.return_value
    mock_ingestion.extract_all.return_value = {
        "jobs": {
            "job_1": {"duration": 3},
            "job_2": {"duration": 5},
        }
    }

    # ---- Mock scheduler results ----
    mock_scheduler = mock_scheduler_class.return_value
    mock_scheduler.solve.return_value = {
        "job_1": {"start": 0, "end": 3},
        "job_2": {"start": 3, "end": 8},
    }

    # ---- Run main ----
    app.main()

    # ---- Capture output ----
    captured = capsys.readouterr()

    # ---- Assertions ----
    assert "Schedule Results:" in captured.out
    assert "job_1" in captured.out
    assert "job_2" in captured.out

    # Ensure ingestion and scheduler were called
    mock_ingestion.extract_all.assert_called_once()
    mock_scheduler.solve.assert_called_once()


@patch("app.DataIngestion")
@patch("app.DBTable")
def test_main_no_jobs_exits(mock_dbtable_class, mock_data_ingestion_class):
    mock_dbtable_class.return_value.get_connection.return_value = MagicMock()
    mock_data_ingestion_class.return_value.extract_all.return_value = {
        "jobs": {}
    }

    with pytest.raises(SystemExit):
        app.main()



@patch("app.DBTable")
@patch("app.DataIngestion")
@patch("app.SchedulerDataInput")
@patch("app.SchedulerConstraint")
@patch("app.SchedulerObjective")
@patch("app.SchedulerModelBuilder")
@patch("app.Scheduler")
def test_main_correctly_wires_scheduler_components(
    mock_scheduler_class,
    mock_model_builder_class,
    mock_objective_class,
    mock_constraint_class,
    mock_data_input_class,
    mock_ingestion_class,
    mock_dbtable_class,
):
    """
    Verifies that:
    - Jobs are passed correctly into SchedulerDataInput
    - Constraints and objectives are registered
    - Scheduler is built with correct components
    """

    # ---- DB ----
    mock_dbtable_class.return_value.get_connection.return_value = MagicMock()

    # ---- Extracted jobs ----
    jobs_data = {
        "job_A": {"duration": 2},
        "job_B": {"duration": 4},
    }
    mock_ingestion_class.return_value.extract_all.return_value = {
        "jobs": jobs_data
    }

    # ---- SchedulerDataInput ----
    mock_data_input = MagicMock()
    mock_data_input.validate_input.return_value = True
    mock_data_input_class.return_value = mock_data_input

    # ---- Constraints ----
    mock_constraints = MagicMock()
    mock_constraint_class.return_value = mock_constraints

    # ---- Objective ----
    mock_objective = MagicMock()
    mock_objective_class.return_value = mock_objective

    # ---- Scheduler result ----
    mock_scheduler_class.return_value.solve.return_value = {}

    # ---- Run main ----
    app.main()

    # ================= ASSERTIONS =================

    # Jobs added correctly
    expected_calls = [
        call("job_A", {"duration": 2}),
        call("job_B", {"duration": 4}),
    ]
    mock_data_input.add_jobs.assert_has_calls(expected_calls, any_order=True)

    # Input validation happened
    mock_data_input.validate_input.assert_called_once()

    # Constraint registered
    mock_constraints.add_constraint.assert_called_once_with(
        mock_constraint_class.no_overlap_constraint
    )

    # Objective registered
    mock_objective.add_objective.assert_called_once_with(
        mock_objective_class.minimize_makespan
    )

    # Scheduler constructed with correct objects
    mock_scheduler_class.assert_called_once_with(
        mock_data_input,
        mock_constraints,
        mock_model_builder_class.return_value,
        mock_objective,
    )

    # Scheduler executed
    mock_scheduler_class.return_value.solve.assert_called_once()
