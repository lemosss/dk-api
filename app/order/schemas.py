from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


# ============ Company Schemas ============
class CompanyCreate(BaseModel):
    name: str
    cnpj: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    cnpj: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class CompanyOut(BaseModel):
    id: int
    name: str
    cnpj: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Invoice Schemas ============
class InvoiceCreate(BaseModel):
    company_id: int
    description: str
    amount: float
    due_date: date
    file_url: Optional[str] = None
    notes: Optional[str] = None


class InvoiceUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    due_date: Optional[date] = None
    file_url: Optional[str] = None
    notes: Optional[str] = None
    is_paid: Optional[bool] = None


class InvoiceOut(BaseModel):
    id: int
    company_id: int
    description: str
    amount: float
    due_date: date
    file_url: Optional[str]
    is_paid: bool
    paid_at: Optional[datetime]
    notes: Optional[str]
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceWithCompany(InvoiceOut):
    company_name: Optional[str] = None
