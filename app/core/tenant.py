from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User, RoleEnum
from app.models.company import Company
from app.core.dependencies import get_current_user


def get_company_from_path(
    company_key: str,
    db: Session = Depends(get_db)
) -> Company:
    """
    Busca a empresa pelo company_key da URL.
    Usado em rotas como /{company_key}/...
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


def get_current_tenant(
    company: Company = Depends(get_company_from_path),
    current_user: User = Depends(get_current_user)
) -> Company:
    """
    Valida que o usuário atual tem permissão para acessar o tenant (empresa).
    
    - SuperAdmin: acesso a qualquer empresa
    - Admin/User: apenas sua própria empresa
    """
    # Super admin tem acesso a qualquer empresa
    if current_user.role == RoleEnum.superadmin:
        return company
    
    # Admin/User só pode acessar sua própria empresa
    if current_user.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar esta empresa"
        )
    
    return company


def require_tenant_admin(
    company: Company = Depends(get_current_tenant),
    current_user: User = Depends(get_current_user)
) -> Company:
    """
    Requer que o usuário seja admin da empresa ou superadmin.
    """
    if current_user.role not in [RoleEnum.superadmin, RoleEnum.admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem realizar esta ação"
        )
    
    return company


def get_optional_tenant(
    company_key: str = None,
    db: Session = Depends(get_db)
) -> Company | None:
    """
    Busca a empresa opcionalmente (para rotas que podem funcionar com ou sem tenant).
    """
    if not company_key:
        return None
    
    company = db.query(Company).filter(
        Company.company_key == company_key,
        Company.is_active == True
    ).first()
    
    return company
