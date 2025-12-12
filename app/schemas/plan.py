from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
import re

from app.models.plan import PlanEnum
from app.schemas.user import UserOut


class PlanBase(BaseModel):
    name: PlanEnum
    display_name: str
    price: Decimal
    max_clients: int
    features: Optional[list[str]] = None


class PlanCreate(PlanBase):
    pass


class PlanOut(BaseModel):
    id: int
    name: PlanEnum
    display_name: str
    price: Decimal
    max_clients: int
    features: Optional[list[str]]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PlanPublic(BaseModel):
    """Informações públicas do plano para landing page"""
    id: int
    name: str
    display_name: str
    price: Decimal
    max_clients: int
    features: Optional[list[str]]

    class Config:
        from_attributes = True


class RegisterRequest(BaseModel):
    """Request para autocadastro de empresa + usuário admin"""
    # Dados do usuário
    email: EmailStr
    password: str
    name: str

    # Dados da empresa
    company_name: str
    company_key: str
    cnpj: str

    # Plano (opcional, default: starter)
    plan_id: Optional[int] = None

    @field_validator('company_key')
    @classmethod
    def validate_company_key(cls, v: str) -> str:
        """Valida que company_key é um slug válido"""
        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', v):
            raise ValueError(
                'company_key deve ser um slug válido '
                '(apenas letras minúsculas, números e hífens)'
            )
        if len(v) < 3:
            raise ValueError('company_key deve ter pelo menos 3 caracteres')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Valida força da senha"""
        if len(v) < 6:
            raise ValueError('Senha deve ter pelo menos 6 caracteres')
        return v

    @field_validator('cnpj')
    @classmethod
    def validate_cnpj(cls, v: str) -> str:
        """Valida formato do CNPJ"""
        # Remove caracteres não numéricos
        cnpj_digits = re.sub(r'\D', '', v)
        if len(cnpj_digits) != 14:
            raise ValueError('CNPJ deve ter 14 dígitos')
        return v


class RegisterResponse(BaseModel):
    """Response do autocadastro com token e dados do usuário"""
    access_token: str
    token_type: str = "bearer"
    company_key: str
    user: UserOut
