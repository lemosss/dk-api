from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from app.db.database import get_db
from app.models.invoice import Invoice
from app.models.company import Company
from app.models.user import User
from app.core.tenant import get_current_tenant
from app.core.dependencies import get_current_user

router = APIRouter(tags=["tenant-dashboard"])


@router.get("/{company_key}/dashboard")
def get_tenant_dashboard(
    company: Company = Depends(get_current_tenant),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dashboard da empresa com métricas e resumos.
    """
    today = date.today()
    
    # Total de faturas
    total_invoices = db.query(func.count(Invoice.id)).filter(
        Invoice.company_id == company.id
    ).scalar() or 0
    
    # Total a receber (não pagas)
    total_pending = db.query(func.sum(Invoice.amount)).filter(
        Invoice.company_id == company.id,
        Invoice.is_paid == False
    ).scalar() or 0
    
    # Total recebido (pagas)
    total_received = db.query(func.sum(Invoice.amount)).filter(
        Invoice.company_id == company.id,
        Invoice.is_paid == True
    ).scalar() or 0
    
    # Faturas vencidas
    overdue_count = db.query(func.count(Invoice.id)).filter(
        Invoice.company_id == company.id,
        Invoice.is_paid == False,
        Invoice.due_date < today
    ).scalar() or 0
    
    overdue_amount = db.query(func.sum(Invoice.amount)).filter(
        Invoice.company_id == company.id,
        Invoice.is_paid == False,
        Invoice.due_date < today
    ).scalar() or 0
    
    # Faturas vencendo em 7 dias
    next_week = today + timedelta(days=7)
    upcoming_count = db.query(func.count(Invoice.id)).filter(
        Invoice.company_id == company.id,
        Invoice.is_paid == False,
        Invoice.due_date >= today,
        Invoice.due_date <= next_week
    ).scalar() or 0
    
    upcoming_amount = db.query(func.sum(Invoice.amount)).filter(
        Invoice.company_id == company.id,
        Invoice.is_paid == False,
        Invoice.due_date >= today,
        Invoice.due_date <= next_week
    ).scalar() or 0
    
    # Total de usuários da empresa
    total_users = db.query(func.count(User.id)).filter(
        User.company_id == company.id
    ).scalar() or 0
    
    # Últimas 5 faturas
    recent_invoices = db.query(Invoice).filter(
        Invoice.company_id == company.id
    ).order_by(Invoice.created_at.desc()).limit(5).all()
    
    return {
        "company": {
            "id": company.id,
            "name": company.name,
            "company_key": company.company_key
        },
        "summary": {
            "total_invoices": total_invoices,
            "total_pending": float(total_pending),
            "total_received": float(total_received),
            "total_users": total_users
        },
        "overdue": {
            "count": overdue_count,
            "amount": float(overdue_amount)
        },
        "upcoming": {
            "count": upcoming_count,
            "amount": float(upcoming_amount)
        },
        "recent_invoices": [
            {
                "id": inv.id,
                "description": inv.description,
                "amount": float(inv.amount),
                "due_date": inv.due_date.isoformat(),
                "is_paid": inv.is_paid
            }
            for inv in recent_invoices
        ]
    }
