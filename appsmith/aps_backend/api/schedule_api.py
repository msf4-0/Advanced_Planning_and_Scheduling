from fastapi import APIRouter, Body
from service import Schedule
from models import ScheduleRequest

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
    schedule = Schedule()
    gantt_schedule = schedule.get_gantt_friendly_schedule()
    return gantt_schedule

