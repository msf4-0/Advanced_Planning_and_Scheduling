import json
import logging
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from repository import DBTable
from schema_mapper import SchemaMapper
from data_ingestion import DataIngestion
from scheduler import SchedulerDataInput, SchedulerModelBuilder, SchedulerConstraint, SchedulerObjective, Scheduler
from configs import Configs

from api import (
    admin_api,
    graph_api,
    table_api
)
class SchedulerInput(BaseModel):
	config: Optional[Dict[str, Any]] = None
	data: Optional[Dict[str, Any]] = None
	
db = DBTable()

app = FastAPI()

# app.include_router(aps_api.router)
app.include_router(admin_api.router)
app.include_router(graph_api.router)
app.include_router(table_api.router)

@app.post(
		"/run_scheduler",
		tags=["Schedule"]
		)
def run_scheduler_endpoint(input: SchedulerInput = Body(None)):
	try:
		db = DBTable()
		schema = SchemaMapper(db.get_connection())
		# Only update mapping if config is present and not empty

		if input and input.config and isinstance(input.config, dict) and input.config:
			logging.info(f"(API) Updating schema mapping with config: {input.config}")
			schema.update_mapping(input.config, use_db=False)

		result = main()
		
		db.add("schedule_result", {"result": json.dumps(result)})

		return {"success": True, "result": result}
	except Exception as e:
		logging.error(f"(API) Error running scheduler: {e}")
		raise HTTPException(status_code=500, detail=str(e))
	
@app.get(
		"/recent-schedule",
		tags=["Schedule"]
)
def get_schedule():
	'''
	Fetch the most recent schedule result.

	Location: appsmith/aps_backend/api/aps_api.py
	'''
	try:
		db = DBTable()
		result = db.fetch("schedule_result")
		# If result is a list, get the latest
		latest = result[-1] if result else {}
		# Convert JSON string back to dict if needed
		if latest and isinstance(latest, dict) and "result" in latest:
			try:
				latest["result"] = json.loads(latest["result"])
			except Exception:
				pass
		return {"success": True, "result": latest}
	except Exception as e:
		logging.error(f"(API) Error fetching recent schedule: {e}")
		raise HTTPException(status_code=500, detail=str(e))

@app.post(
		"/toggle-run-scheduler",
		tags=["Schedule"]
		)
def toggle_run_scheduler():
	'''
	Toggles the scheduler's running state.

	Location: appsmith/aps_backend/api/aps_api.py
	'''
	try:
		db = DBTable()
		current_state = db.fetch("config", {"key": "toggle_autoRun"})
		new_state = not (current_state[0]["value"] == "TRUE") if current_state else True
		db.update("config", {"value": "TRUE" if new_state else "FALSE"}, {"key": "toggle_autoRun"})
		return {"success": True, "is_running": new_state}
	except Exception as e:
		logging.error(f"(API) Error toggling scheduler state: {e}")
		raise HTTPException(status_code=500, detail=str(e))
	
@app.get(
		"/get-scheduler-state",
		tags=["Schedule"]
		)
def get_scheduler_state():
	'''
	Fetches the current running state of the scheduler.

	Location: appsmith/aps_backend/api/aps_api.py
	'''
	try:
		db = DBTable()
		current_state = db.fetch("config", {"key": "toggle_autoRun"})
		is_running = True if (current_state[0]["value"] == "TRUE") else False
		return {"success": True, "is_running": is_running}
	except Exception as e:
		logging.error(f"(API) Error fetching scheduler state: {e}")
		raise HTTPException(status_code=500, detail=str(e))


# --------------- Scheduler main application (non-API) --------------- #

# Main entry point for running data extraction and scheduling (no API)

mock_data = {
	'jobs': {
		'jobA': {
			'duration': 5,
			'allowed_machines': [1, 2],
			'domain': (0, 20),
			'predecessor': None,
			'due_date': 15,
			'qty_ordered': 100,
			'qty_initialized': 90,
			'locked': False
		},
		'jobB': {
			'duration': 7,
			'allowed_machines': [2],
			'domain': (0, 25),
			'predecessor': 'jobA',
			'due_date': 20,
			'qty_ordered': 120,
			'qty_initialized': 110,
			'locked': False
		},
		'jobC': {
			'duration': 4,
			'allowed_machines': [1],
			'domain': (0, 18),
			'predecessor': None,
			'due_date': 10,
			'qty_ordered': 80,
			'qty_initialized': 80,
			'locked': True,
			'locked_start': 2,
			'locked_machine': 1
		},
		'jobD': {
			'duration': 10,
			'allowed_machines': [2, 3],
			'domain': (0, 20),
			'predecessor': None,
			'due_date': 15,
			'qty_ordered': 100,
			'qty_initialized': 90,
			'locked': False
		},
		'jobE': {
			'duration': 15,
			'allowed_machines': [3],
			'domain': (0, 20),
			'predecessor': None,
			'due_date': 15,
			'qty_ordered': 100,
			'qty_initialized': 90,
			'locked': False
		},
	},
	'machines': {
		1: {
			'type': 'CNC',
			'capacity': 2
		},
		2: {
			'type': 'Lathe',
			'capacity': 1
		},
		3: {
			'type': 'Milling',
			'capacity': 1
		}
	},
	'materials': {
		'matA': {
			'material_name': 'Steel'
		},
		'matB': {
			'material_name': 'Aluminum'
		}
	}
}

logging.basicConfig(level=logging.INFO)

def main():
	# Database connection
	# conn = DBTable().get_connection_graph()
	conn = DBTable().get_connection()
	logging.info("Database connection established.")

	# Initialize schema mapper and data ingestion
	mapper = SchemaMapper(conn)
	# logging.info(f"(APP) Current mapping config: {mapper.get_mapping()}")
	ingestion = DataIngestion(mapper)


	# Extract all data for the scheduler
	extracted = ingestion.extract_all()
	logging.info(f"Extracted data: {extracted}")

	jobs = extracted.get('jobs', {})
	logging.info(f"Extracted jobs: {jobs}")

	# jobs = mock_data['jobs']
	# You can add machines/materials extraction as needed

	# Prepare scheduler input
	data_input = SchedulerDataInput()
	for job_id, props in jobs.items():
		logging.info(f"Adding job {job_id} with props {props}")
		data_input.add_jobs(job_id, props)

	# Validate input
	if not data_input.validate_input():
		raise ValueError("(app.py) Invalid scheduler input data.")

	# Set up constraints and objectives (add more as needed)
	constraints = SchedulerConstraint()
	objective = SchedulerObjective()

	# Configs(constraints, objective, mapper.get_mapping())  # Register built-in constraints and objectives
	# You can pass a static mapping or mock config if needed
	Configs(constraints, objective, {})  # Register built-in constraints and objectives

	# Build model and run scheduler
	model_builder = SchedulerModelBuilder(data_input, constraints, objective)
	scheduler = Scheduler(data_input, constraints, model_builder, objective)
	results = scheduler.solve()

	if results:
		return results
	else:
		raise ValueError("No feasible schedule found.")
	

if __name__ == "__main__":
	output = main()
	if output is not None:
		print(output)
	else:
		print("No feasible schedule found.")


