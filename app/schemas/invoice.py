from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class InvoiceBase(BaseModel):
    company_id: int
    description: str
    amount: float
    due_date: date
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    file_url: Optional[str] = None


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
