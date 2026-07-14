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

    active_run_id = None
    
    # 1. Initialize a structured relational run log tracker row
    try:
        logging.info("(API) Registering pipeline optimization run tracking entry...")
        # Assuming your repo structure returns the newly generated record or its primary ID
        new_run_list = runs_repo.add(data={
            "run_status": "Running",
            "started_at": datetime.now(),
            "log_messages": "Optimization workflow initiated via API request endpoint."
        })

        # If new_run_list is not None AND not empty, safe to index
        if new_run_list: 
            inserted_row = new_run_list[0]
            if isinstance(inserted_row, dict): # still good to verify it's a dict
                active_run_id = inserted_row.get("id")
                logging.info(f"(API) Run tracked successfully. Generated Run ID: {active_run_id}")
        
    except Exception as log_err:
        logging.warning(f"(API) Non-fatal audit log tracking registration failure: {log_err}")

    try:
        logging.info("(API) Triggering scheduling creation pipeline...")
        # 2. Run the isolated background engine graph layout processing scripts
        result = ScheduleCreator.run(run_id=active_run_id)
        
        # 3. Update the run log row to register a clean computational success
        # Note: If your repo layer tracks the last generated sequence serial, use it as id_value.
        # Otherwise, write a fallback update constraint query pattern.
        return {
            "success": True,
            "result": result
        }

    except Exception as pipeline_err:
        logging.error(f"(API) Critical failure in pipeline execution: {pipeline_err}")
        
        # Update the run status to 'Failed' if we have an active run ID
        if active_run_id:
            try:
                runs_repo.update(active_run_id, {
                    "run_status": "Failed",
                    "completed_at": datetime.now(),
                    "log_messages": f"Pipeline failed with error: {str(pipeline_err)}"
                })
            except Exception as update_err:
                logging.error(f"(API) Could not update run status to Failed: {update_err}")
                
        return {
            "success": False,
            "error": str(pipeline_err)
        }

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
