from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from contextlib import asynccontextmanager
from pathlib import Path

from app.database import engine, Base
from app.routes import auth_router, users_router, companies_router, invoices_router

# Get the base directory (project root)
# This file is at backend/app/main.py, so we go up 2 levels to reach project root
BASE_DIR = Path(__file__).parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown


app = FastAPI(
    title="DK Invoice Calendar",
    description="Sistema de gestão de faturas com calendário",
    version="2.0.0",
    lifespan=lifespan
)

# Static files
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")

# Templates
templates = Jinja2Templates(directory=str(FRONTEND_DIR / "templates"))

# API Routes
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(companies_router)
app.include_router(invoices_router)


# ============ Page Routes ============
@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/login")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/calendar", response_class=HTMLResponse)
async def calendar_page(request: Request):
    return templates.TemplateResponse("calendar.html", {"request": request})


@app.get("/invoices", response_class=HTMLResponse)
async def invoices_page(request: Request):
    return templates.TemplateResponse("invoices.html", {"request": request})


@app.get("/companies", response_class=HTMLResponse)
async def companies_page(request: Request):
    return templates.TemplateResponse("companies.html", {"request": request})


@app.get("/users", response_class=HTMLResponse)
async def users_page(request: Request):
    return templates.TemplateResponse("users.html", {"request": request})
