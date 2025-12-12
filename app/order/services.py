from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from typing import Optional
import os

from app.order.models import Company, Invoice
from app.order.schemas import CompanyCreate, CompanyUpdate, InvoiceCreate, InvoiceUpdate, InvoiceOut, InvoiceWithCompany
from app.user.models import RoleEnum, User


# ============ Company Services ============
def get_company_by_id(db: Session, company_id: int) -> Company:
    """Get company by ID"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return company


def get_company_by_cnpj(db: Session, cnpj: str) -> Company | None:
    """Get company by CNPJ"""
    return db.query(Company).filter(Company.cnpj == cnpj).first()


def get_all_companies(db: Session) -> list[Company]:
    """Get all companies"""
    return db.query(Company).all()


def get_user_companies(db: Session, user: User) -> list[Company]:
    """Get companies accessible to user"""
    if user.role == RoleEnum.user:
        return db.query(Company).filter(Company.id == user.company_id).all()
    return get_all_companies(db)


def create_new_company(db: Session, company_data: CompanyCreate) -> Company:
    """Create a new company"""
    if get_company_by_cnpj(db, company_data.cnpj):
        raise HTTPException(status_code=400, detail="CNPJ já cadastrado")
    
    company = Company(**company_data.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def update_company_data(db: Session, company_id: int, company_data: CompanyUpdate) -> Company:
    """Update company data"""
    company = get_company_by_id(db, company_id)
    for key, value in company_data.model_dump(exclude_unset=True).items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return company


def delete_company_by_id(db: Session, company_id: int) -> None:
    """Delete company by ID"""
    company = get_company_by_id(db, company_id)
    db.delete(company)
    db.commit()


# ============ Invoice Services ============
def get_invoice_by_id(db: Session, invoice_id: int) -> Invoice:
    """Get invoice by ID"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    return invoice


def get_all_invoices(
    db: Session,
    user: User,
    company_id: Optional[int] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    is_paid: Optional[bool] = None
) -> list[tuple[Invoice, str]]:
    """Get all invoices with filters"""
    from sqlalchemy import extract
    
    query = db.query(Invoice, Company.name.label("company_name")).join(Company)
    
    if user.role == RoleEnum.user:
        query = query.filter(Invoice.company_id == user.company_id)
    elif company_id:
        query = query.filter(Invoice.company_id == company_id)
    
    if month and year:
        query = query.filter(
            extract('month', Invoice.due_date) == month,
            extract('year', Invoice.due_date) == year
        )
    
    if is_paid is not None:
        query = query.filter(Invoice.is_paid == is_paid)
    
    return query.order_by(Invoice.due_date).all()


def get_invoices_by_date(
    db: Session,
    user: User,
    target_date: str,
    company_id: Optional[int] = None
) -> list[tuple[Invoice, str]]:
    """Get invoices for a specific date"""
    from datetime import datetime as dt
    try:
        date_obj = dt.strptime(target_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Data inválida. Use YYYY-MM-DD")
    
    query = db.query(Invoice, Company.name.label("company_name")).join(Company)
    query = query.filter(Invoice.due_date == date_obj)
    
    if user.role == RoleEnum.user:
        query = query.filter(Invoice.company_id == user.company_id)
    elif company_id:
        query = query.filter(Invoice.company_id == company_id)
    
    return query.order_by(Invoice.amount.desc()).all()


def create_new_invoice(db: Session, invoice_data: InvoiceCreate, created_by: int) -> Invoice:
    """Create a new invoice"""
    invoice = Invoice(**invoice_data.model_dump(), created_by=created_by)
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


def update_invoice_data(db: Session, invoice_id: int, invoice_data: InvoiceUpdate) -> Invoice:
    """Update invoice data"""
    invoice = get_invoice_by_id(db, invoice_id)
    
    update_data = invoice_data.model_dump(exclude_unset=True)
    
    # If marking as paid, register date
    if "is_paid" in update_data:
        if update_data["is_paid"] and not invoice.is_paid:
            invoice.paid_at = datetime.utcnow()
        elif not update_data["is_paid"]:
            invoice.paid_at = None
    
    for key, value in update_data.items():
        setattr(invoice, key, value)
    
    db.commit()
    db.refresh(invoice)
    return invoice


def toggle_invoice_paid(db: Session, invoice_id: int) -> Invoice:
    """Toggle invoice paid status"""
    invoice = get_invoice_by_id(db, invoice_id)
    invoice.is_paid = not invoice.is_paid
    invoice.paid_at = datetime.utcnow() if invoice.is_paid else None
    db.commit()
    db.refresh(invoice)
    return invoice


def delete_invoice_by_id(db: Session, invoice_id: int) -> None:
    """Delete invoice by ID"""
    invoice = get_invoice_by_id(db, invoice_id)
    db.delete(invoice)
    db.commit()


def update_invoice_file(db: Session, invoice_id: int, file_url: str, old_file_path: Optional[str] = None) -> Invoice:
    """Update invoice file URL and remove old file if exists"""
    invoice = get_invoice_by_id(db, invoice_id)
    
    # Remove old file if exists
    if old_file_path and os.path.exists(old_file_path):
        try:
            os.remove(old_file_path)
        except:
            pass
    
    invoice.file_url = file_url
    db.commit()
    db.refresh(invoice)
    return invoice


def remove_invoice_file(db: Session, invoice_id: int, file_path: str) -> None:
    """Remove invoice file"""
    invoice = get_invoice_by_id(db, invoice_id)
    
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except:
            pass
    
    invoice.file_url = None
    db.commit()


def check_invoice_access(user: User, invoice: Invoice) -> None:
    """Check if user has access to invoice"""
    if user.role == RoleEnum.user and invoice.company_id != user.company_id:
        raise HTTPException(status_code=403, detail="Permissão negada")


def check_company_access(user: User, company_id: int) -> None:
    """Check if user has access to company"""
    if user.role == RoleEnum.user and user.company_id != company_id:
        raise HTTPException(status_code=403, detail="Permissão negada")
