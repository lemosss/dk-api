from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
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
    """List companies (users see only their company, admins see their company, superadmin sees all)"""
    company_service = CompanyService(db)
    
    if current_user.role == RoleEnum.superadmin:
        # Superadmin vê todas as empresas
        return company_service.get_all_companies()
    
    # Admin e User veem apenas sua própria empresa
    if not current_user.company_id:
        return []
    company = company_service.get_company_by_id(current_user.company_id)
    return [company]


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
    current_user: User = Depends(require_roles(RoleEnum.superadmin))
):
    """Create a new company (SuperAdmin only)"""
    company_service = CompanyService(db)
    return company_service.create_company(company_data)


@router.put("/{company_id}", response_model=CompanyOut)
def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.superadmin))
):
    """Update a company (SuperAdmin only)"""
    company_service = CompanyService(db)
    return company_service.update_company(company_id, company_data)


@router.post("/{company_id}/logo", response_model=CompanyOut)
async def upload_company_logo(
    company_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.superadmin))
):
    """Upload company logo (SuperAdmin only)"""
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de imagem inválido. Use JPEG, PNG, WEBP ou GIF."
        )
    
    # Create directory if not exists
    logos_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "uploads", "logos")
    os.makedirs(logos_dir, exist_ok=True)
    
    # Generate unique filename
    ext = file.filename.split(".")[-1] if "." in file.filename else "png"
    filename = f"{company_id}_{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(logos_dir, filename)
    
    # Save file
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)
    
    # Update company
    company_service = CompanyService(db)
    logo_url = f"/uploads/logos/{filename}"
    return company_service.update_logo(company_id, logo_url)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.superadmin))
):
    """Delete a company (SuperAdmin only)"""
    company_service = CompanyService(db)
    company_service.delete_company(company_id)
    return None
