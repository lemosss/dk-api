from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.token import Token
from app.schemas.company import CompanyPublicInfo
from app.models.company import Company
from app.models.user import User, RoleEnum
from app.core.security import verify_password, create_access_token

router = APIRouter(tags=["tenant-auth"])


@router.get("/{company_key}/info", response_model=CompanyPublicInfo)
def get_company_public_info(
    company_key: str,
    db: Session = Depends(get_db)
):
    """
    Retorna informações públicas da empresa para tela de login.
    Não requer autenticação.
    """
    company = db.query(Company).filter(
        Company.company_key == company_key,
        Company.is_active == True
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    return company


@router.post("/{company_key}/auth/login", response_model=Token)
def tenant_login(
    company_key: str,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login específico por empresa.
    
    Valida que o usuário pertence à empresa ou é superadmin.
    """
    # Busca empresa
    company = db.query(Company).filter(
        Company.company_key == company_key,
        Company.is_active == True
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    # Busca usuário
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    # Valida que usuário pertence à empresa (ou é superadmin)
    if user.role != RoleEnum.superadmin and user.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Você não tem acesso a esta empresa"
        )
    
    # Se for superadmin, retorna flag para redirecionar para admin
    if user.role == RoleEnum.superadmin:
        access_token = create_access_token({
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value
        })
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "redirect_to_admin": True
        }
    
    # Gera token com claims da empresa
    access_token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "company_id": company.id,
        "company_key": company_key
    })
    
    return {"access_token": access_token, "token_type": "bearer"}
