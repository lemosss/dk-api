from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceOut, InvoiceWithCompany
from app.services.invoice_service import InvoiceService
from app.core.dependencies import require_roles, get_current_user
from app.models.user import User, RoleEnum
from app.utils.file_handler import FileHandler

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("/", response_model=List[InvoiceWithCompany])
def list_invoices(
    company_id: Optional[int] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    is_paid: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List invoices with optional filters"""
    invoice_service = InvoiceService(db)
    
    # Users can only see invoices from their company
    if current_user.role == RoleEnum.user:
        company_id = current_user.company_id
    
    return invoice_service.get_all_invoices(
        company_id=company_id,
        month=month,
        year=year,
        is_paid=is_paid
    )


@router.get("/calendar")
def get_calendar(
    month: int,
    year: int,
    company_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get calendar data for a specific month"""
    invoice_service = InvoiceService(db)
    
    # Users can only see their company's data
    if current_user.role == RoleEnum.user:
        company_id = current_user.company_id
    
    return invoice_service.get_calendar_data(month, year, company_id)


@router.get("/by-date")
def get_invoices_by_date(
    date: str,
    company_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get invoices for a specific date"""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data inválida. Use YYYY-MM-DD"
        )
    
    invoice_service = InvoiceService(db)
    
    # Users can only see their company's data
    if current_user.role == RoleEnum.user:
        company_id = current_user.company_id
    
    return invoice_service.get_invoices_by_date(target_date, company_id)


@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific invoice"""
    invoice_service = InvoiceService(db)
    invoice = invoice_service.get_invoice_by_id(invoice_id)
    
    # Users can only access invoices from their company
    if current_user.role == RoleEnum.user and invoice.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada"
        )
    
    return invoice


@router.post("/", response_model=InvoiceOut, status_code=status.HTTP_201_CREATED)
def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.admin, RoleEnum.superadmin))
):
    """Create a new invoice (Admin only)"""
    invoice_service = InvoiceService(db)
    return invoice_service.create_invoice(invoice_data, current_user.id)


@router.put("/{invoice_id}", response_model=InvoiceOut)
def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.admin, RoleEnum.superadmin))
):
    """Update an invoice (Admin only)"""
    invoice_service = InvoiceService(db)
    return invoice_service.update_invoice(invoice_id, invoice_data)


@router.patch("/{invoice_id}/toggle-paid", response_model=InvoiceOut)
def toggle_paid(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle paid status of an invoice"""
    invoice_service = InvoiceService(db)
    invoice = invoice_service.get_invoice_by_id(invoice_id)
    
    # Users can only toggle invoices from their company
    if current_user.role == RoleEnum.user and invoice.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada"
        )
    
    return invoice_service.toggle_paid_status(invoice_id)


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.admin, RoleEnum.superadmin))
):
    """Delete an invoice (Admin only)"""
    invoice_service = InvoiceService(db)
    invoice_service.delete_invoice(invoice_id)
    return None


@router.post("/{invoice_id}/upload")
async def upload_invoice_file(
    invoice_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.admin, RoleEnum.superadmin))
):
    """Upload PDF file for an invoice (Admin only)"""
    invoice_service = InvoiceService(db)
    invoice = invoice_service.get_invoice_by_id(invoice_id)
    
    # Delete old file if exists
    if invoice.file_url:
        FileHandler.delete_file(invoice.file_url)
    
    # Save new file
    file_url = await FileHandler.save_file(file)
    
    # Update invoice with new file URL
    invoice = invoice_service.update_invoice(invoice_id, InvoiceUpdate(file_url=file_url))
    
    return {"ok": True, "file_url": file_url}
