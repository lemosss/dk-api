from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.db.database import engine
from app.models import Base
from app.api.v1.router import api_router
from app.api.tenant.router import tenant_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: Cleanup if needed


app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema de gestão de faturas multi-tenant com calendário - API REST",
    version="2.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory as static files
uploads_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Include API router (admin global routes)
app.include_router(api_router, prefix="/api/v1")

# Include Tenant router (company-specific routes)
# Rotas: /{company_key}/info, /{company_key}/auth/login, /{company_key}/dashboard, etc.
app.include_router(tenant_router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "DK Invoice Calendar API - Multi-Tenant",
        "version": "2.1.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
