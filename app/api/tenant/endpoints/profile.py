from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.db.database import get_db
from app.models.user import User, RoleEnum
from app.models.company import Company
from app.core.tenant import get_current_tenant, require_tenant_admin
from app.core.dependencies import get_current_user


router = APIRouter(tags=["tenant-profile"])


class CompanyProfileUpdate(BaseModel):
    """Schema para admin atualizar perfil da empresa"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None


class CompanyProfileOut(BaseModel):
    """Schema de resposta do perfil da empresa"""
    id: int
    company_key: str
    name: str
    cnpj: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    logo_url: Optional[str]
    primary_color: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True


@router.get("/{company_key}/profile", response_model=CompanyProfileOut)
def get_company_profile(
    company: Company = Depends(get_current_tenant),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna perfil da empresa.
    Qualquer usuário autenticado da empresa pode ver.
    """
    return company


@router.put("/{company_key}/profile", response_model=CompanyProfileOut)
def update_company_profile(
    profile_data: CompanyProfileUpdate,
    company: Company = Depends(require_tenant_admin),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza perfil da empresa (logo e cor primária).
    Apenas admin da empresa ou superadmin podem editar.
    """
    # Atualizar campos
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(company, field, value)
    
    db.commit()
    db.refresh(company)
    
    return company
