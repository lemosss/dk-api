from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List

from app.common.database import get_db
from app.user.models import User, RoleEnum
from app.user.schemas import Token, UserCreate, UserUpdate, UserOut
from app.user.auth import decode_access_token
from app.user import services


# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Routers
auth_router = APIRouter(prefix="/api/auth", tags=["auth"])
users_router = APIRouter(prefix="/api/users", tags=["users"])


# ============ Dependencies ============
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    """Get current authenticated user from token"""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = services.get_user_by_id(db, int(payload.get("sub")))
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuário inativo")
    return user


def require_roles(*roles: RoleEnum):
    """Dependency to check if user has required role"""
    def checker(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Permissão negada")
        return user
    return checker


# ============ Auth Routes ============
@auth_router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login endpoint - authenticate user and return JWT token"""
    user = services.authenticate_user(db, form_data.username, form_data.password)
    token = services.create_user_token(user)
    return {"access_token": token, "token_type": "bearer"}


@auth_router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    """Get current user information"""
    return user


# ============ Users Routes ============
@users_router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), user: User = Depends(require_roles(RoleEnum.superadmin, RoleEnum.admin))):
    """List all users (admin/superadmin only)"""
    return services.get_all_users(db)


@users_router.post("/", response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(RoleEnum.superadmin))):
    """Create new user (superadmin only)"""
    return services.create_new_user(db, payload)


@users_router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), user: User = Depends(require_roles(RoleEnum.superadmin))):
    """Update user (superadmin only)"""
    return services.update_user_data(db, user_id, payload)


@users_router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(RoleEnum.superadmin))):
    """Delete user (superadmin only)"""
    services.delete_user_by_id(db, user_id)
    return {"ok": True}
