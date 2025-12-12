from typing import Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import extract
from app.models.invoice import Invoice
from app.repositories.base import BaseRepository


class InvoiceRepository(BaseRepository[Invoice]):
    """Repository for Invoice model"""
    
    def __init__(self, db: Session):
        super().__init__(Invoice, db)
    
    def get_by_company(self, company_id: int) -> list[Invoice]:
        """Get all invoices for a specific company"""
        return self.db.query(Invoice).filter(Invoice.company_id == company_id).all()
    
    def get_paid_invoices(self) -> list[Invoice]:
        """Get all paid invoices"""
        return self.db.query(Invoice).filter(Invoice.is_paid == True).all()
    
    def get_unpaid_invoices(self) -> list[Invoice]:
        """Get all unpaid invoices"""
        return self.db.query(Invoice).filter(Invoice.is_paid == False).all()
    
    def get_overdue_invoices(self, current_date: date = None) -> list[Invoice]:
        """Get all overdue unpaid invoices"""
        if current_date is None:
            current_date = date.today()
        return self.db.query(Invoice).filter(
            Invoice.is_paid == False,
            Invoice.due_date < current_date
        ).all()
    
    def get_by_month_year(self, month: int, year: int, company_id: Optional[int] = None) -> list[Invoice]:
        """Get invoices for a specific month and year"""
        query = self.db.query(Invoice).filter(
            extract('month', Invoice.due_date) == month,
            extract('year', Invoice.due_date) == year
        )
        if company_id:
            query = query.filter(Invoice.company_id == company_id)
        return query.all()
    
    def get_by_date(self, target_date: date, company_id: Optional[int] = None) -> list[Invoice]:
        """Get invoices for a specific date"""
        query = self.db.query(Invoice).filter(Invoice.due_date == target_date)
        if company_id:
            query = query.filter(Invoice.company_id == company_id)
        return query.order_by(Invoice.amount.desc()).all()
