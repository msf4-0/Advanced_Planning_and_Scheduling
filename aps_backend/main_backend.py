import json
import logging
import uvicorn

from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, Body, Query, BackgroundTasks
from pydantic import BaseModel

from repository import Repository

from classes import ScheduleCreator

class SchedulerInput(BaseModel):
    config: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None

app = FastAPI(title="APS Production Scheduling Engine API")
logging.basicConfig(level=logging.INFO)

@app.post("/run_scheduler", tags=["Schedule"])
def run_scheduler_endpoint(input_payload: SchedulerInput = Body(None)):
    """
    API Endpoint: Executes the detached ScheduleCreator pipeline,
    waitr for changed, and updates DB tables.
    """

    try:
        logging.info("(API) Triggering scheduling creation pipeline...")
        result = ScheduleCreator.run()
        return {
            "success": True,
            "result": result
        }

    except ValueError as e:
        logging.error(f"(API) Scheduler constraint configuration error: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logging.error(f"(API) Fatal backend server execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recent-schedule", tags=["Schedule"])
def get_schedule():
    """
    Fetch the most recent schedule logging result from database table.
    """

    try:
        result_repository = Repository(table_name="schedule_result")
        result = result_repository.fetch_all()
        latest = result[-1] if result else {}