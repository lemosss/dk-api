from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    company_key: Optional[str] = None  # Para redirecionar usuário para sua empresa
    redirect_to_admin: Optional[bool] = None  # Para redirecionar superadmin para admin


class TokenData(BaseModel):
    user_id: int | None = None
    role: str | None = None
