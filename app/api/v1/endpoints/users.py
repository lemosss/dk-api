from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.services.user_service import UserService
from app.core.dependencies import require_roles, get_current_user
from app.models.user import User, RoleEnum

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.superadmin))
):
    """List all users (SuperAdmin only)"""
    user_service = UserService(db)
    return user_service.get_all_users()


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.superadmin))
):
    """Get a specific user (SuperAdmin only)"""
    user_service = UserService(db)
    return user_service.get_user_by_id(user_id)


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.superadmin))
):
    """Create a new user (SuperAdmin only)"""
    user_service = UserService(db)
    return user_service.create_user(user_data)


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.superadmin))
):
    """Update a user (SuperAdmin only)"""
    user_service = UserService(db)
    return user_service.update_user(user_id, user_data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.superadmin))
):
    """Delete a user (SuperAdmin only)"""
    user_service = UserService(db)
    user_service.delete_user(user_id)
    return None
