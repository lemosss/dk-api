from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.user.models import RoleEnum


# ============ Auth Schemas ============
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None
    role: RoleEnum = RoleEnum.user
    company_id: Optional[int] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[RoleEnum] = None
    company_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    email: str
    name: Optional[str]
    role: RoleEnum
    company_id: Optional[int]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
