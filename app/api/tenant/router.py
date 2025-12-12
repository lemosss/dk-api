from fastapi import APIRouter
from app.api.tenant.endpoints import auth, invoices, users, dashboard, profile

tenant_router = APIRouter()

# Rotas públicas (info da empresa, login)
tenant_router.include_router(auth.router)

# Rotas protegidas por tenant
tenant_router.include_router(dashboard.router)
tenant_router.include_router(invoices.router)
tenant_router.include_router(users.router)
tenant_router.include_router(profile.router)
