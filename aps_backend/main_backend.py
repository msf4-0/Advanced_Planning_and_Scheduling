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
    Fetch the complete schedule details (meta run information + all scheduled tasks)
    of the most recent successful schedule run.
    """

    try:
        config = DatabaseConfig()
        conn_manager = ConnectionManager(config)
        
        runs_repo = Repository("scheduling_runs", conn_manager)
        tasks_repo = Repository("scheduled_tasks", conn_manager)
        
        # 1. Fetch all runs to find the latest successful execution
        all_runs = runs_repo.fetch_all()
        successful_runs = [r for r in all_runs if r.get("run_status") == "Success"]
        
        if not successful_runs:
            return {
                "success": True,
                "message": "No successful schedule runs found yet.",
                "run_info": {},
                "tasks": []
            }
            
        # Get the latest run status details
        latest_run = successful_runs[-1]
        run_id = latest_run.get("id")
        
        # 2. Fetch all scheduled tasks and filter them by the latest run_id
        all_tasks = tasks_repo.fetch_all()
        latest_tasks = [t for t in all_tasks if t.get("run_id") == run_id]
        
        return {
            "success": True,
            "run_info": latest_run,
            "tasks": latest_tasks
        }
        
    except Exception as e:
        logging.error(f"(API) Error fetching recent schedule and associated tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main_backend:app", host="0.0.0.0", port=8000, reload=True)