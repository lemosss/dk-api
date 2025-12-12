from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date, timedelta
from typing import Dict

from app.order.models import Invoice
from app.user.models import User, RoleEnum


def get_dashboard_stats(db: Session, user: User) -> Dict:
    """Get dashboard statistics for user"""
    query = db.query(Invoice)
    if user.role == RoleEnum.user:
        query = query.filter(Invoice.company_id == user.company_id)
    
    total = query.count()
    paid = query.filter(Invoice.is_paid == True).count()
    pending = query.filter(Invoice.is_paid == False).count()
    
    # Overdue unpaid invoices
    overdue = query.filter(Invoice.is_paid == False, Invoice.due_date < date.today()).count()
    
    # Total pending amount
    pending_amount = db.query(func.sum(Invoice.amount)).filter(
        Invoice.is_paid == False
    )
    if user.role == RoleEnum.user:
        pending_amount = pending_amount.filter(Invoice.company_id == user.company_id)
    pending_amount = pending_amount.scalar() or 0
    
    # Upcoming invoices (next 7 days)
    upcoming = query.filter(
        Invoice.is_paid == False,
        Invoice.due_date >= date.today(),
        Invoice.due_date <= date.today() + timedelta(days=7)
    ).count()
    
    return {
        "total": total,
        "paid": paid,
        "pending": pending,
        "overdue": overdue,
        "upcoming": upcoming,
        "pending_amount": float(pending_amount)
    }


def get_calendar_data(db: Session, user: User, month: int, year: int, company_id: int = None) -> Dict:
    """Get calendar data for a specific month"""
    query = db.query(Invoice)
    
    if user.role == RoleEnum.user:
        query = query.filter(Invoice.company_id == user.company_id)
    elif company_id:
        query = query.filter(Invoice.company_id == company_id)
    
    query = query.filter(
        extract('month', Invoice.due_date) == month,
        extract('year', Invoice.due_date) == year
    )
    
    invoices = query.all()
    
    # Group by day - use string keys for JSON compatibility
    days = {}
    for inv in invoices:
        day = str(inv.due_date.day)  # Convert to string
        if day not in days:
            days[day] = {"total": 0, "paid": 0, "pending": 0, "amount": 0}
        days[day]["total"] += 1
        days[day]["amount"] += float(inv.amount)
        if inv.is_paid:
            days[day]["paid"] += 1
        else:
            days[day]["pending"] += 1
    
    return {"month": month, "year": year, "days": days}
