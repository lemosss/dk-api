from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import os
import uuid

from app.database import get_db
from app.models import User, Company, Invoice, RoleEnum
from app.schemas import (
    Token, UserCreate, UserUpdate, UserOut,
    CompanyCreate, CompanyUpdate, CompanyOut,
    InvoiceCreate, InvoiceUpdate, InvoiceOut, InvoiceWithCompany
)
from app.auth import hash_password, verify_password, create_access_token, decode_access_token

# Upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Routers
auth_router = APIRouter(prefix="/api/auth", tags=["auth"])
users_router = APIRouter(prefix="/api/users", tags=["users"])
companies_router = APIRouter(prefix="/api/companies", tags=["companies"])
invoices_router = APIRouter(prefix="/api/invoices", tags=["invoices"])


# ============ Dependencies ============
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuário inativo")
    return user


def require_roles(*roles: RoleEnum):
    def checker(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Permissão negada")
        return user
    return checker


# ============ Auth Routes ============
@auth_router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuário inativo")
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return {"access_token": token, "token_type": "bearer"}


@auth_router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


# ============ Users Routes ============
@users_router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), user: User = Depends(require_roles(RoleEnum.superadmin, RoleEnum.admin))):
    return db.query(User).all()


@users_router.post("/", response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(RoleEnum.superadmin))):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    new_user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        name=payload.name,
        role=payload.role,
        company_id=payload.company_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@users_router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), user: User = Depends(require_roles(RoleEnum.superadmin))):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(target, key, value)
    db.commit()
    db.refresh(target)
    return target


@users_router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(RoleEnum.superadmin))):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    db.delete(target)
    db.commit()
    return {"ok": True}


# ============ Companies Routes ============
@companies_router.get("/", response_model=List[CompanyOut])
def list_companies(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role == RoleEnum.user:
        return db.query(Company).filter(Company.id == user.company_id).all()
    return db.query(Company).all()


@companies_router.get("/{company_id}", response_model=CompanyOut)
def get_company(company_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    if user.role == RoleEnum.user and user.company_id != company_id:
        raise HTTPException(status_code=403, detail="Permissão negada")
    return company


@companies_router.post("/", response_model=CompanyOut)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(RoleEnum.superadmin, RoleEnum.admin))):
    if db.query(Company).filter(Company.cnpj == payload.cnpj).first():
        raise HTTPException(status_code=400, detail="CNPJ já cadastrado")
    company = Company(**payload.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@companies_router.put("/{company_id}", response_model=CompanyOut)
def update_company(company_id: int, payload: CompanyUpdate, db: Session = Depends(get_db), user: User = Depends(require_roles(RoleEnum.superadmin, RoleEnum.admin))):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return company


@companies_router.delete("/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(RoleEnum.superadmin))):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    db.delete(company)
    db.commit()
    return {"ok": True}


# ============ Invoices Routes ============
@invoices_router.get("/", response_model=List[InvoiceWithCompany])
def list_invoices(
    company_id: int = None,
    month: int = None,
    year: int = None,
    is_paid: bool = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = db.query(Invoice, Company.name.label("company_name")).join(Company)
    
    if user.role == RoleEnum.user:
        query = query.filter(Invoice.company_id == user.company_id)
    elif company_id:
        query = query.filter(Invoice.company_id == company_id)
    
    if month and year:
        from sqlalchemy import extract
        query = query.filter(
            extract('month', Invoice.due_date) == month,
            extract('year', Invoice.due_date) == year
        )
    
    if is_paid is not None:
        query = query.filter(Invoice.is_paid == is_paid)
    
    results = query.order_by(Invoice.due_date).all()
    
    invoices = []
    for inv, company_name in results:
        inv_dict = InvoiceOut.model_validate(inv).model_dump()
        inv_dict["company_name"] = company_name
        invoices.append(InvoiceWithCompany(**inv_dict))
    
    return invoices


@invoices_router.get("/calendar")
def get_calendar(
    month: int,
    year: int,
    company_id: int = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Retorna dados para o calendário: dias com faturas e contagens"""
    from sqlalchemy import extract, func
    
    query = db.query(Invoice)
    
    if user.role == RoleEnum.user:
        query = query.filter(Invoice.company_id == user.company_id)
    elif company_id:
        query = query.filter(Invoice.company_id == company_id)
    
    query = query.filter(
        extract('month', Invoice.due_date) == month,
        extract('year', Invoice.due_date) == year
    )
    
    invoices = query.all()
    
    # Agrupar por dia
    days = {}
    for inv in invoices:
        day = inv.due_date.day
        if day not in days:
            days[day] = {"total": 0, "paid": 0, "pending": 0, "amount": 0}
        days[day]["total"] += 1
        days[day]["amount"] += float(inv.amount)
        if inv.is_paid:
            days[day]["paid"] += 1
        else:
            days[day]["pending"] += 1
    
    return {"month": month, "year": year, "days": days}


@invoices_router.get("/by-date")
def get_invoices_by_date(
    date: str,
    company_id: int = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Retorna faturas de um dia específico"""
    from datetime import datetime as dt
    try:
        target_date = dt.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Data inválida. Use YYYY-MM-DD")
    
    query = db.query(Invoice, Company.name.label("company_name")).join(Company)
    query = query.filter(Invoice.due_date == target_date)
    
    if user.role == RoleEnum.user:
        query = query.filter(Invoice.company_id == user.company_id)
    elif company_id:
        query = query.filter(Invoice.company_id == company_id)
    
    results = query.order_by(Invoice.amount.desc()).all()
    
    invoices = []
    for inv, company_name in results:
        inv_dict = InvoiceOut.model_validate(inv).model_dump()
        inv_dict["company_name"] = company_name
        invoices.append(inv_dict)
    
    return invoices


@invoices_router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    if user.role == RoleEnum.user and invoice.company_id != user.company_id:
        raise HTTPException(status_code=403, detail="Permissão negada")
    return invoice


@invoices_router.post("/", response_model=InvoiceOut)
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(RoleEnum.superadmin, RoleEnum.admin))):
    invoice = Invoice(**payload.model_dump(), created_by=user.id)
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


@invoices_router.post("/{invoice_id}/upload")
async def upload_invoice_file(
    invoice_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(RoleEnum.superadmin, RoleEnum.admin))
):
    """Upload de arquivo PDF para a fatura (boleto)"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    
    # Validar tipo de arquivo
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são permitidos")
    
    # Gerar nome único para o arquivo
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Salvar arquivo
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {str(e)}")
    
    # Remover arquivo antigo se existir
    if invoice.file_url and invoice.file_url.startswith("/static/uploads/"):
        old_file = os.path.join(os.path.dirname(__file__), invoice.file_url.lstrip("/").replace("app/", ""))
        if os.path.exists(old_file):
            try:
                os.remove(old_file)
            except:
                pass
    
    # Atualizar URL no banco
    invoice.file_url = f"/static/uploads/{unique_filename}"
    db.commit()
    db.refresh(invoice)
    
    return {"ok": True, "file_url": invoice.file_url}


@invoices_router.delete("/{invoice_id}/file")
def delete_invoice_file(
    invoice_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(RoleEnum.superadmin, RoleEnum.admin))
):
    """Remove arquivo da fatura"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    
    if invoice.file_url and invoice.file_url.startswith("/static/uploads/"):
        file_path = os.path.join(UPLOAD_DIR, os.path.basename(invoice.file_url))
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
    
    invoice.file_url = None
    db.commit()
    
    return {"ok": True}


@invoices_router.put("/{invoice_id}", response_model=InvoiceOut)
def update_invoice(invoice_id: int, payload: InvoiceUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    if user.role == RoleEnum.user and invoice.company_id != user.company_id:
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    update_data = payload.model_dump(exclude_unset=True)
    
    # Se está marcando como pago, registrar data
    if "is_paid" in update_data:
        if update_data["is_paid"] and not invoice.is_paid:
            invoice.paid_at = datetime.utcnow()
        elif not update_data["is_paid"]:
            invoice.paid_at = None
    
    for key, value in update_data.items():
        setattr(invoice, key, value)
    
    db.commit()
    db.refresh(invoice)
    return invoice


@invoices_router.patch("/{invoice_id}/toggle-paid", response_model=InvoiceOut)
def toggle_paid(invoice_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Toggle status de pagamento"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    if user.role == RoleEnum.user and invoice.company_id != user.company_id:
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    invoice.is_paid = not invoice.is_paid
    invoice.paid_at = datetime.utcnow() if invoice.is_paid else None
    
    db.commit()
    db.refresh(invoice)
    return invoice


@invoices_router.delete("/{invoice_id}")
def delete_invoice(invoice_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(RoleEnum.superadmin, RoleEnum.admin))):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    db.delete(invoice)
    db.commit()
    return {"ok": True}


# ============ Dashboard Stats ============
@auth_router.get("/stats")
def get_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Estatísticas para o dashboard"""
    from sqlalchemy import func
    from datetime import date
    
    query = db.query(Invoice)
    if user.role == RoleEnum.user:
        query = query.filter(Invoice.company_id == user.company_id)
    
    total = query.count()
    paid = query.filter(Invoice.is_paid == True).count()
    pending = query.filter(Invoice.is_paid == False).count()
    
    # Vencidas não pagas
    overdue = query.filter(Invoice.is_paid == False, Invoice.due_date < date.today()).count()
    
    # Valor total pendente
    pending_amount = db.query(func.sum(Invoice.amount)).filter(
        Invoice.is_paid == False
    )
    if user.role == RoleEnum.user:
        pending_amount = pending_amount.filter(Invoice.company_id == user.company_id)
    pending_amount = pending_amount.scalar() or 0
    
    # Próximas a vencer (7 dias)
    from datetime import timedelta
    upcoming = query.filter(
        Invoice.is_paid == False,
        Invoice.due_date >= date.today(),
        Invoice.due_date <= date.today() + timedelta(days=7)
    ).count()
    
    return {
        "total": total,
        "paid": paid,
        "pending": pending,
        "overdue": overdue,
        "upcoming": upcoming,
        "pending_amount": float(pending_amount)
    }
