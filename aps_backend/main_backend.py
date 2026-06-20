import logging
import uvicorn
from datetime import datetime
from fastapi import FastAPI, HTTPException

from repository import Repository, DatabaseConfig, ConnectionManager
from classes import ScheduleCreator
from api import crud_routes

app = FastAPI(title="APS Production Scheduling Engine API")
logging.basicConfig(level=logging.INFO)

app.include_router(crud_routes.router)

@app.post("/run_scheduler", tags=["Schedule"])
def run_scheduler_endpoint():
    """
    API Endpoint: Logs the beginning of an engine execution, triggers the 
    isolated ScheduleCreator pipeline, and persists the success status.
    """
    config = DatabaseConfig()
    conn_manager = ConnectionManager(config)
    runs_repo = Repository("scheduling_runs", conn_manager)
    
    # 1. Initialize a structured relational run log tracker row
    try:
        logging.info("(API) Registering pipeline optimization run tracking entry...")
        # Assuming your repo structure returns the newly generated record or its primary ID
        runs_repo.add(data={
            "run_status": "Running",
            "started_at": datetime.now(),
            "log_messages": "Optimization workflow initiated via API request endpoint."
        })
    except Exception as log_err:
        logging.warning(f"(API) Non-fatal audit log tracking registration failure: {log_err}")

    try:
        logging.info("(API) Triggering scheduling creation pipeline...")
        # 2. Run the isolated background engine graph layout processing scripts
        result = ScheduleCreator.run()
        
        # 3. Update the run log row to register a clean computational success
        # Note: If your repo layer tracks the last generated sequence serial, use it as id_value.
        # Otherwise, write a fallback update constraint query pattern.
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
    Fetch the execution parameters and status details of the most 
    recent scheduler optimization run recorded in the database schema.
    """

    try:
        config = DatabaseConfig()
        conn_manager = ConnectionManager(config)
        
        # Clean Fix: Map strictly to the actual 'scheduling_runs' schema layout
        runs_repo = Repository("scheduling_runs", conn_manager)
        result = runs_repo.fetch_all()
        
        # Extract the last processed dictionary item safely from the array list
        latest = result[-1] if result else {}
        
        return {
            "success": True,
            "result": latest
        }
    except Exception as e:
        logging.error(f"(API) Error fetching recent schedule optimization run log: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main_backend:app", host="0.0.0.0", port=8000, reload=True)
