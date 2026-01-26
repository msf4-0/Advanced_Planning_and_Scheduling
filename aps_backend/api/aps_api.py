from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
# Import your scheduler logic (adjust as needed)
from app import main as scheduler_main

router = APIRouter()

# Example input model for running the scheduler
class SchedulerInput(BaseModel):
	config: Dict[str, Any]
	data: Dict[str, Any]

# Health check endpoint
@router.get(
		"/status",
		tags=["Schedule"]
		)
def status():
	return {"status": "ok"}

# Run the scheduler
@router.post(
		"/run_scheduler",
		tags=["Schedule"]
		)
def run_scheduler_endpoint(input: SchedulerInput):
	try:
		result = scheduler_main()
		return {"success": True, "result": result}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

# # Get the latest schedule result
# @router.get("/get_schedule")
# def get_schedule():
# 	try:
# 		result = scheduler_main.get_latest_schedule_result()
# 		return {"success": True, "result": result}
# 	except Exception as e:
# 		raise HTTPException(status_code=500, detail=str(e))
