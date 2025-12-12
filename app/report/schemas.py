from pydantic import BaseModel
from typing import Dict


class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total: int
    paid: int
    pending: int
    overdue: int
    upcoming: int
    pending_amount: float


class CalendarData(BaseModel):
    """Calendar data for a specific month"""
    month: int
    year: int
    days: Dict[int, Dict[str, int | float]]
