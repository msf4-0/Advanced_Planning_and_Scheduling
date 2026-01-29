import logging
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


# Run the scheduler
@router.post(
		"/run_scheduler",
		tags=["Schedule"]
		)
def run_scheduler_endpoint(input: SchedulerInput = Body(None)):
	try:
		schema = SchemaMapper(DBTable().get_connection_graph())
		# Only update mapping if config is present and not empty

		if input and input.config and isinstance(input.config, dict) and input.config:
			logging.info(f"(API) Updating schema mapping with config: {input.config}")
			schema.update_mapping(input.config, use_db=False)

		result = scheduler_main()
		return {"success": True, "result": result}
	except Exception as e:
		logging.error(f"(API) Error running scheduler: {e}")
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
