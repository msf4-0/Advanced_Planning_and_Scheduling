from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

# Import your scheduler logic (adjust as needed)
from main import run_scheduler, get_latest_schedule_result

app = FastAPI(title="APS Backend API Gateway")

# Example input model for running the scheduler
class SchedulerInput(BaseModel):
	config: Dict[str, Any]
	data: Dict[str, Any]

# Health check endpoint
@app.get("/status")
def status():
	return {"status": "ok"}

# Run the scheduler
@app.post("/run_scheduler")
def run_scheduler_endpoint(input: SchedulerInput):
	try:
		result = run_scheduler(input.config, input.data)
		return {"success": True, "result": result}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

# Get the latest schedule result
@app.get("/get_schedule")
def get_schedule():
	try:
		result = get_latest_schedule_result()
		return {"success": True, "result": result}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

# (Optional) Add more endpoints for config, constraints, etc.

if __name__ == "__main__":
	uvicorn.run("aps_api:app", host="0.0.0.0", port=8000, reload=True)
