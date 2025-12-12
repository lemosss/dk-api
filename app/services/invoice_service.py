from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import Optional
from app.models.invoice import Invoice
from app.models.company import Company
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceWithCompany
from app.repositories.invoice_repository import InvoiceRepository


class InvoiceService:
    """Service for invoice management operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.invoice_repo = InvoiceRepository(db)
    
    def get_all_invoices(
        self,
        company_id: Optional[int] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        is_paid: Optional[bool] = None
    ) -> list[InvoiceWithCompany]:
        """Get all invoices with optional filters"""
        if month and year:
            invoices = self.invoice_repo.get_by_month_year(month, year, company_id)
        elif company_id:
            invoices = self.invoice_repo.get_by_company(company_id)
        else:
            invoices = self.invoice_repo.get_all()
        
        # Filter by paid status if specified
        if is_paid is not None:
            invoices = [inv for inv in invoices if inv.is_paid == is_paid]
        
        # Add company name to each invoice
        result = []
        for invoice in invoices:
            invoice_dict = {
                "id": invoice.id,
                "company_id": invoice.company_id,
                "description": invoice.description,
                "amount": float(invoice.amount),
                "due_date": invoice.due_date,
                "file_url": invoice.file_url,
                "is_paid": invoice.is_paid,
                "paid_at": invoice.paid_at,
                "notes": invoice.notes,
                "created_by": invoice.created_by,
                "created_at": invoice.created_at,
                "company_name": invoice.company.name if invoice.company else None
            }
            result.append(InvoiceWithCompany(**invoice_dict))
        
        return result
    
    def get_invoice_by_id(self, invoice_id: int) -> Invoice:
        """Get invoice by ID"""
        invoice = self.invoice_repo.get(invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fatura não encontrada"
            )
        return invoice
    
    def create_invoice(self, invoice_data: InvoiceCreate, created_by: int) -> Invoice:
        """Create a new invoice"""
        invoice = Invoice(
            **invoice_data.model_dump(),
            created_by=created_by
        )
        return self.invoice_repo.create(invoice)
    
    def update_invoice(self, invoice_id: int, invoice_data: InvoiceUpdate) -> Invoice:
        """Update an existing invoice"""
        invoice = self.get_invoice_by_id(invoice_id)
        
        update_data = invoice_data.model_dump(exclude_unset=True)
        
        # Handle paid_at timestamp
        if "is_paid" in update_data:
            if update_data["is_paid"] and not invoice.is_paid:
                update_data["paid_at"] = datetime.utcnow()
            elif not update_data["is_paid"]:
                update_data["paid_at"] = None
        
        return self.invoice_repo.update(invoice, update_data)
    
    def toggle_paid_status(self, invoice_id: int) -> Invoice:
        """Toggle the paid status of an invoice"""
        invoice = self.get_invoice_by_id(invoice_id)
        
        update_data = {
            "is_paid": not invoice.is_paid,
            "paid_at": datetime.utcnow() if not invoice.is_paid else None
        }
        
        return self.invoice_repo.update(invoice, update_data)
    
    def delete_invoice(self, invoice_id: int) -> bool:
        """Delete an invoice"""
        invoice = self.get_invoice_by_id(invoice_id)
        return self.invoice_repo.delete(invoice.id)
    
    def get_calendar_data(
        self,
        month: int,
        year: int,
        company_id: Optional[int] = None
    ) -> dict:
        """Get calendar data for a specific month"""
        invoices = self.invoice_repo.get_by_month_year(month, year, company_id)
        
        # Group by day
        days = {}
        for inv in invoices:
            day = inv.due_date.day
            if day not in days:
                days[day] = {"total": 0, "paid": 0, "pending": 0, "amount": 0}
            days[day]["total"] += 1
            days[day]["amount"] += float(inv.amount)
            if inv.is_paid:
                days[day]["paid"] += 1
            else:
                days[day]["pending"] += 1
        
        return {"month": month, "year": year, "days": days}
    
    def get_invoices_by_date(
        self,
        target_date: date,
        company_id: Optional[int] = None
    ) -> list[dict]:
        """Get invoices for a specific date"""
        invoices = self.invoice_repo.get_by_date(target_date, company_id)
        
        result = []
        for invoice in invoices:
            invoice_dict = {
                "id": invoice.id,
                "company_id": invoice.company_id,
                "description": invoice.description,
                "amount": float(invoice.amount),
                "due_date": invoice.due_date,
                "file_url": invoice.file_url,
                "is_paid": invoice.is_paid,
                "paid_at": invoice.paid_at,
                "notes": invoice.notes,
                "created_by": invoice.created_by,
                "created_at": invoice.created_at,
                "company_name": invoice.company.name if invoice.company else None
            }
            result.append(invoice_dict)
        
        return result
    
    def get_dashboard_stats(self, company_id: Optional[int] = None) -> dict:
        """Get dashboard statistics"""
        if company_id:
            invoices = self.invoice_repo.get_by_company(company_id)
        else:
            invoices = self.invoice_repo.get_all()
        
        total = len(invoices)
        paid = len([inv for inv in invoices if inv.is_paid])
        pending = len([inv for inv in invoices if not inv.is_paid])
        
        # Overdue unpaid
        today = date.today()
        overdue = len([inv for inv in invoices if not inv.is_paid and inv.due_date < today])
        
        # Pending amount
        pending_amount = sum(float(inv.amount) for inv in invoices if not inv.is_paid)
        
        # Upcoming (next 7 days)
        from datetime import timedelta
        upcoming_date = today + timedelta(days=7)
        upcoming = len([
            inv for inv in invoices
            if not inv.is_paid and today <= inv.due_date <= upcoming_date
        ])
        
        return {
            "total": total,
            "paid": paid,
            "pending": pending,
            "overdue": overdue,
            "upcoming": upcoming,
            "pending_amount": pending_amount
        }
