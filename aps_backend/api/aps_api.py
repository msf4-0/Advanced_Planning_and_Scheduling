import logging
import json
from fastapi import APIRouter, HTTPException, Request, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any
# Import your scheduler logic (adjust as needed)
from app import main as scheduler_main
from schema_mapper import SchemaMapper
from repository import DBTable

router = APIRouter()

# Example input model for running the scheduler
class SchedulerInput(BaseModel):
	config: Optional[Dict[str, Any]] = None
	data: Optional[Dict[str, Any]] = None

@router.post(
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
	
@router.get(
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

# Run the scheduler
@router.post(
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

		result = scheduler_main()
		
		db.add("schedule_result", {"result": json.dumps(result)})

		return {"success": True, "result": result}
	except Exception as e:
		logging.error(f"(API) Error running scheduler: {e}")
		raise HTTPException(status_code=500, detail=str(e))
	
@router.get(
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

@router.get(
		"/get-config",
		tags=["Schedule"]
		)
def get_scheduler_config():
	'''
	Fetch the current scheduler configuration.

	Location: appsmith/aps_backend/api/aps_api.py
	'''
	try:
		schema = SchemaMapper(DBTable().get_connection_graph())
		config = schema.get_mapping()
		return {"success": True, "config": config}
	except Exception as e:
		logging.error(f"(API) Error fetching scheduler config: {e}")
		raise HTTPException(status_code=500, detail=str(e))


# # Get the latest schedule result
# @router.get("/get_schedule")
# def get_schedule():
# 	try:
# 		result = scheduler_main.get_latest_schedule_result()
# 		return {"success": True, "result": result}
# 	except Exception as e:
# 		raise HTTPException(status_code=500, detail=str(e))
