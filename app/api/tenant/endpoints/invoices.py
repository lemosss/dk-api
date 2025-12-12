from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from typing import List, Optional
from datetime import date
from app.db.database import get_db
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceOut
from app.models.invoice import Invoice
from app.models.company import Company
from app.models.user import User, RoleEnum
from app.core.tenant import get_current_tenant
from app.core.dependencies import get_current_user

router = APIRouter(tags=["tenant-invoices"])


# IMPORTANTE: Rotas específicas ANTES de rotas com parâmetros dinâmicos
@router.get("/{company_key}/invoices/calendar")
def get_tenant_calendar(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000),
    company: Company = Depends(get_current_tenant),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna dados do calendário de faturas da empresa"""
    invoices = db.query(Invoice).filter(
        Invoice.company_id == company.id,
        extract('month', Invoice.due_date) == month,
        extract('year', Invoice.due_date) == year
    ).all()
    
    days = {}
    for invoice in invoices:
        day = invoice.due_date.day
        if day not in days:
            days[day] = {"pending": 0, "paid": 0, "total": 0}
        
        days[day]["total"] += 1
        if invoice.is_paid:
            days[day]["paid"] += 1
        else:
            days[day]["pending"] += 1
    
    return {"days": days, "month": month, "year": year}


@router.get("/{company_key}/invoices/by-date", response_model=List[InvoiceOut])
def get_tenant_invoices_by_date(
    date: date = Query(...),
    company: Company = Depends(get_current_tenant),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna faturas de um dia específico da empresa"""
    invoices = db.query(Invoice).filter(
        Invoice.company_id == company.id,
        Invoice.due_date == date
    ).all()
    
    return invoices


@router.get("/{company_key}/invoices", response_model=List[InvoiceOut])
def list_tenant_invoices(
    company: Company = Depends(get_current_tenant),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista faturas da empresa do tenant"""
    return db.query(Invoice).filter(Invoice.company_id == company.id).all()


@router.get("/{company_key}/invoices/{invoice_id}", response_model=InvoiceOut)
def get_tenant_invoice(
    invoice_id: int,
    company: Company = Depends(get_current_tenant),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Busca uma fatura específica da empresa"""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.company_id == company.id
    ).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fatura não encontrada"
        )
    
    return invoice


@router.post("/{company_key}/invoices", response_model=InvoiceOut, status_code=status.HTTP_201_CREATED)
def create_tenant_invoice(
    invoice_data: InvoiceCreate,
    company: Company = Depends(get_current_tenant),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria uma nova fatura para a empresa (apenas admin)"""
    # Verificar se é admin ou superadmin
    if current_user.role not in [RoleEnum.admin, RoleEnum.superadmin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem criar faturas"
        )
    
    invoice = Invoice(
        company_id=company.id,
        description=invoice_data.description,
        amount=invoice_data.amount,
        due_date=invoice_data.due_date,
        is_paid=invoice_data.is_paid if invoice_data.is_paid is not None else False,
        notes=invoice_data.notes,
        created_by=current_user.id
    )
    
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    
    return invoice


@router.put("/{company_key}/invoices/{invoice_id}", response_model=InvoiceOut)
def update_tenant_invoice(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    company: Company = Depends(get_current_tenant),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza uma fatura da empresa (apenas admin)"""
    # Verificar se é admin ou superadmin
    if current_user.role not in [RoleEnum.admin, RoleEnum.superadmin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem editar faturas"
        )
    
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.company_id == company.id
    ).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fatura não encontrada"
        )
    
    update_data = invoice_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(invoice, field, value)
    
    db.commit()
    db.refresh(invoice)
    
    return invoice


@router.delete("/{company_key}/invoices/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant_invoice(
    invoice_id: int,
    company: Company = Depends(get_current_tenant),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exclui uma fatura da empresa (apenas admin)"""
    # Verificar se é admin ou superadmin
    if current_user.role not in [RoleEnum.admin, RoleEnum.superadmin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem excluir faturas"
        )
    
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.company_id == company.id
    ).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fatura não encontrada"
        )
    
    db.delete(invoice)
    db.commit()
    
    return None


@router.patch("/{company_key}/invoices/{invoice_id}/toggle-paid", response_model=InvoiceOut)
def toggle_tenant_invoice_paid(
    invoice_id: int,
    company: Company = Depends(get_current_tenant),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Alterna o status de pagamento de uma fatura (qualquer usuário autenticado da empresa)"""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.company_id == company.id
    ).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fatura não encontrada"
        )
    
    invoice.is_paid = not invoice.is_paid
    db.commit()
    db.refresh(invoice)
    
    return invoice
