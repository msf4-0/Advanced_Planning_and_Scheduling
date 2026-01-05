from typing_extensions import Optional
from fastapi import APIRouter, Body
from service.scheduler import Schedule
from repository import DBTable, GraphEditor  # Make sure to import your connection getter

router = APIRouter()

@router.post("/schedule/run", response_model=dict)
def initiate_scheduling(schedule_horizon: Optional[int] = Body(...)):
    """
    Initiates the scheduling process by creating a Schedule object
    and calling its schedule method.

    Location: appsmith/aps_backend/api/schedule_api.py
    """
    schedule = Schedule()
    result = schedule.create_schedule()
    return result