from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.invoice_service import InvoiceService
from app.core.dependencies import get_current_user
from app.models.user import User, RoleEnum

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics"""
    invoice_service = InvoiceService(db)
    
    # Users can only see stats for their company
    company_id = None
    if current_user.role == RoleEnum.user:
        company_id = current_user.company_id
    
    return invoice_service.get_dashboard_stats(company_id)
