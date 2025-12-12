from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import re


class CompanyBase(BaseModel):
    name: str
    cnpj: str
    company_key: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    primary_color: Optional[str] = "#3B82F6"
    
    @field_validator('company_key')
    @classmethod
    def validate_company_key(cls, v: str) -> str:
        """Valida que company_key é um slug válido"""
        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', v):
            raise ValueError('company_key deve ser um slug válido (apenas letras minúsculas, números e hífens)')
        if len(v) < 3:
            raise ValueError('company_key deve ter pelo menos 3 caracteres')
        return v


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    cnpj: Optional[str] = None
    company_key: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None
    primary_color: Optional[str] = None
    
    @field_validator('company_key')
    @classmethod
    def validate_company_key(cls, v: Optional[str]) -> Optional[str]:
        """Valida que company_key é um slug válido"""
        if v is None:
            return v
        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', v):
            raise ValueError('company_key deve ser um slug válido (apenas letras minúsculas, números e hífens)')
        if len(v) < 3:
            raise ValueError('company_key deve ter pelo menos 3 caracteres')
        return v


class CompanyOut(BaseModel):
    id: int
    name: str
    cnpj: str
    company_key: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    logo_url: Optional[str]
    primary_color: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CompanyPublicInfo(BaseModel):
    """Informações públicas da empresa para tela de login"""
    name: str
    company_key: str
    logo_url: Optional[str]
    primary_color: Optional[str]
    
    class Config:
        from_attributes = True

