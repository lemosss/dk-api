from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyOut
from app.services.company_service import CompanyService
from app.core.dependencies import require_roles, get_current_user
from app.models.user import User, RoleEnum

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/", response_model=List[CompanyOut])
def list_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List companies (users see only their company, admins see all)"""
    company_service = CompanyService(db)
    
    if current_user.role == RoleEnum.user:
        # Users can only see their own company
        if not current_user.company_id:
            return []
        company = company_service.get_company_by_id(current_user.company_id)
        return [company]
    
    # Admins and superadmins see all companies
    return company_service.get_all_companies()


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific company"""
    company_service = CompanyService(db)
    company = company_service.get_company_by_id(company_id)
    
    # Users can only access their own company
    if current_user.role == RoleEnum.user and current_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada"
        )
    
    return company


@router.post("/", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.admin, RoleEnum.superadmin))
):
    """Create a new company (Admin only)"""
    company_service = CompanyService(db)
    return company_service.create_company(company_data)


@router.put("/{company_id}", response_model=CompanyOut)
def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.admin, RoleEnum.superadmin))
):
    """Update a company (Admin only)"""
    company_service = CompanyService(db)
    return company_service.update_company(company_id, company_data)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.admin, RoleEnum.superadmin))
):
    """Delete a company (Admin only)"""
    company_service = CompanyService(db)
    company_service.delete_company(company_id)
    return None
