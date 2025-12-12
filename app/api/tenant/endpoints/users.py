from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.models.company import Company
from app.models.user import User, RoleEnum
from app.core.tenant import get_current_tenant, require_tenant_admin
from app.core.dependencies import get_current_user
from app.core.security import get_password_hash

router = APIRouter(tags=["tenant-users"])


@router.get("/{company_key}/users", response_model=List[UserOut])
def list_tenant_users(
    company: Company = Depends(require_tenant_admin),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista usuários da empresa.
    Apenas admin da empresa ou superadmin podem ver.
    """
    return db.query(User).filter(User.company_id == company.id).all()


@router.get("/{company_key}/users/{user_id}", response_model=UserOut)
def get_tenant_user(
    user_id: int,
    company: Company = Depends(require_tenant_admin),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Busca um usuário específico da empresa"""
    user = db.query(User).filter(
        User.id == user_id,
        User.company_id == company.id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return user


@router.post("/{company_key}/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_tenant_user(
    user_data: UserCreate,
    company: Company = Depends(require_tenant_admin),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria um novo usuário para a empresa.
    
    - Admin só pode criar usuários com role 'user'
    - SuperAdmin pode criar qualquer role
    """
    # Verifica se email já existe
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Admin só pode criar usuários com role 'user'
    if current_user.role == RoleEnum.admin and user_data.role != RoleEnum.user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode criar usuários com perfil 'user'"
        )
    
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        name=user_data.name,
        role=user_data.role,
        company_id=company.id,  # Força o company_id do tenant
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.put("/{company_key}/users/{user_id}", response_model=UserOut)
def update_tenant_user(
    user_id: int,
    user_data: UserUpdate,
    company: Company = Depends(require_tenant_admin),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza um usuário da empresa"""
    user = db.query(User).filter(
        User.id == user_id,
        User.company_id == company.id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Admin não pode alterar role para algo diferente de 'user'
    if current_user.role == RoleEnum.admin:
        if user_data.role and user_data.role != RoleEnum.user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não pode alterar o perfil para este tipo"
            )
        # Impede alteração de company_id
        if user_data.company_id and user_data.company_id != company.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não pode mover usuários para outra empresa"
            )
    
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/{company_key}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant_user(
    user_id: int,
    company: Company = Depends(require_tenant_admin),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exclui um usuário da empresa"""
    user = db.query(User).filter(
        User.id == user_id,
        User.company_id == company.id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Não pode excluir a si mesmo
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode excluir a si mesmo"
        )
    
    db.delete(user)
    db.commit()
    
    return None
