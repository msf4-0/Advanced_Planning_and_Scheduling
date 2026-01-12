from fastapi import APIRouter, Body, HTTPException
from service import Schedule
from models import ScheduleRequest
from repository import DBTable

router = APIRouter()

@router.post(
        "/schedule/run", 
        response_model=dict,
        tags=["Scheduling"]
        )
def initiate_scheduling(schedule_horizon: ScheduleRequest = Body(None)):
    """
    Initiates the scheduling process by creating a Schedule object
    and calling its schedule method.

    Location: appsmith/aps_backend/api/schedule_api.py
    """
    schedule = Schedule()

    max_horizon = schedule_horizon.schedule_horizon if schedule_horizon and schedule_horizon.schedule_horizon else 480

    schedule_run_id = schedule.create_schedule(max_horizon=max_horizon)
    return {"schedule_run_id": schedule_run_id}

@router.get(
        "/schedule/gantt", 
        response_model=list,
        tags=["Scheduling"]
        )
def get_gantt_schedule():
    """
    Retrieves the Gantt chart friendly schedule.

    Location: appsmith/aps_backend/api/schedule_api.py
    """
    
    table = DBTable()
    schedule_data = table.fetch_schedule_steps()

    if not schedule_data:
        raise HTTPException(status_code=404, detail="No schedule data found.")
    
    return schedule_data


