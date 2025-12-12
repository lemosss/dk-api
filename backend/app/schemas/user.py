from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import RoleEnum


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    role: RoleEnum = RoleEnum.user
    company_id: Optional[int] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
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
