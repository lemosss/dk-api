from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common.database import get_db
from app.user.models import User
from app.user.routes import get_current_user
from app.report.schemas import DashboardStats
from app.report import services


# Router
report_router = APIRouter(prefix="/api", tags=["reports"])


@report_router.get("/auth/stats", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get dashboard statistics"""
    return services.get_dashboard_stats(db, user)
