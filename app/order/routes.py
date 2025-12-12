from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid

from app.common.database import get_db
from app.user.models import User, RoleEnum
from app.user.routes import get_current_user, require_roles
from app.order.models import Company, Invoice
from app.order.schemas import (
    CompanyCreate, CompanyUpdate, CompanyOut,
    InvoiceCreate, InvoiceUpdate, InvoiceOut, InvoiceWithCompany
)
from app.order import services


# Upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Routers
companies_router = APIRouter(prefix="/api/companies", tags=["companies"])
invoices_router = APIRouter(prefix="/api/invoices", tags=["invoices"])


# ============ Companies Routes ============
@companies_router.get("/", response_model=List[CompanyOut])
def list_companies(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """List all companies accessible to user"""
    return services.get_user_companies(db, user)


@companies_router.get("/{company_id}", response_model=CompanyOut)
def get_company(company_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get company by ID"""
    company = services.get_company_by_id(db, company_id)
    services.check_company_access(user, company_id)
    return company


@companies_router.post("/", response_model=CompanyOut)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(RoleEnum.superadmin, RoleEnum.admin))):
    """Create new company (admin/superadmin only)"""
    return services.create_new_company(db, payload)


@companies_router.put("/{company_id}", response_model=CompanyOut)
def update_company(company_id: int, payload: CompanyUpdate, db: Session = Depends(get_db), user: User = Depends(require_roles(RoleEnum.superadmin, RoleEnum.admin))):
    """Update company (admin/superadmin only)"""
    return services.update_company_data(db, company_id, payload)


@companies_router.delete("/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(RoleEnum.superadmin))):
    """Delete company (superadmin only)"""
    services.delete_company_by_id(db, company_id)
    return {"ok": True}


# ============ Invoices Routes ============
@invoices_router.get("/", response_model=List[InvoiceWithCompany])
def list_invoices(
    company_id: int = None,
    month: int = None,
    year: int = None,
    is_paid: bool = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List all invoices with filters"""
    results = services.get_all_invoices(db, user, company_id, month, year, is_paid)
    
    invoices = []
    for inv, company_name in results:
        inv_dict = InvoiceOut.model_validate(inv).model_dump()
        inv_dict["company_name"] = company_name
        invoices.append(InvoiceWithCompany(**inv_dict))
    
    return invoices


@invoices_router.get("/by-date")
def get_invoices_by_date(
    date: str,
    company_id: int = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get invoices for a specific date"""
    results = services.get_invoices_by_date(db, user, date, company_id)
    
    invoices = []
    for inv, company_name in results:
        inv_dict = InvoiceOut.model_validate(inv).model_dump()
        inv_dict["company_name"] = company_name
        invoices.append(inv_dict)
    
    return invoices


@invoices_router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get invoice by ID"""
    invoice = services.get_invoice_by_id(db, invoice_id)
    services.check_invoice_access(user, invoice)
    return invoice


@invoices_router.post("/", response_model=InvoiceOut)
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(RoleEnum.superadmin, RoleEnum.admin))):
    """Create new invoice (admin/superadmin only)"""
    return services.create_new_invoice(db, payload, user.id)


@invoices_router.post("/{invoice_id}/upload")
async def upload_invoice_file(
    invoice_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(RoleEnum.superadmin, RoleEnum.admin))
):
    """Upload PDF file for invoice (admin/superadmin only)"""
    invoice = services.get_invoice_by_id(db, invoice_id)
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são permitidos")
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {str(e)}")
    
    # Get old file path if exists
    old_file_path = None
    if invoice.file_url and invoice.file_url.startswith("/static/uploads/"):
        old_file_path = os.path.join(UPLOAD_DIR, os.path.basename(invoice.file_url))
    
    # Update invoice with new file URL
    new_url = f"/static/uploads/{unique_filename}"
    services.update_invoice_file(db, invoice_id, new_url, old_file_path)
    
    return {"ok": True, "file_url": new_url}


@invoices_router.delete("/{invoice_id}/file")
def delete_invoice_file(
    invoice_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(RoleEnum.superadmin, RoleEnum.admin))
):
    """Remove file from invoice (admin/superadmin only)"""
    invoice = services.get_invoice_by_id(db, invoice_id)
    
    file_path = None
    if invoice.file_url and invoice.file_url.startswith("/static/uploads/"):
        file_path = os.path.join(UPLOAD_DIR, os.path.basename(invoice.file_url))
    
    if file_path:
        services.remove_invoice_file(db, invoice_id, file_path)
    
    return {"ok": True}


@invoices_router.put("/{invoice_id}", response_model=InvoiceOut)
def update_invoice(invoice_id: int, payload: InvoiceUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Update invoice"""
    invoice = services.get_invoice_by_id(db, invoice_id)
    services.check_invoice_access(user, invoice)
    return services.update_invoice_data(db, invoice_id, payload)


@invoices_router.patch("/{invoice_id}/toggle-paid", response_model=InvoiceOut)
def toggle_paid(invoice_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Toggle invoice paid status"""
    invoice = services.get_invoice_by_id(db, invoice_id)
    services.check_invoice_access(user, invoice)
    return services.toggle_invoice_paid(db, invoice_id)


@invoices_router.delete("/{invoice_id}")
def delete_invoice(invoice_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(RoleEnum.superadmin, RoleEnum.admin))):
    """Delete invoice (admin/superadmin only)"""
    services.delete_invoice_by_id(db, invoice_id)
    return {"ok": True}
