from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, companies, invoices, dashboard, register
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(register.router)
api_router.include_router(users.router)
api_router.include_router(companies.router)
api_router.include_router(invoices.router)
api_router.include_router(dashboard.router)
