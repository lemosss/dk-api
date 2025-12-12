from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.plan import RegisterRequest, RegisterResponse, PlanPublic
from app.services.registration_service import RegistrationService
from app.services.plan_service import PlanService

router = APIRouter(tags=["registration"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Public endpoint for self-registration.
    Creates a new company and an admin user.
    Returns JWT token for immediate login.
    """
    service = RegistrationService(db)
    return service.register(data)


@router.get("/plans", response_model=list[PlanPublic])
def list_plans(db: Session = Depends(get_db)):
    """
    Public endpoint to list available plans.
    Used in landing page and registration flow.
    """
    service = PlanService(db)
    return service.get_all_plans()
