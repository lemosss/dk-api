import pytest
from datetime import date, timedelta
from fastapi import HTTPException
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.company_service import CompanyService
from app.services.invoice_service import InvoiceService
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate
from app.models import RoleEnum, Invoice


class TestAuthService:
    """Test AuthService"""
    
    def test_authenticate_user_success(self, db, superadmin_user):
        """Test successful user authentication"""
        service = AuthService(db)
        
        user = service.authenticate_user("superadmin@test.com", "super123")
        
        assert user is not None
        assert user.email == "superadmin@test.com"
    
    def test_authenticate_user_wrong_password(self, db, superadmin_user):
        """Test authentication with wrong password"""
        service = AuthService(db)
        
        with pytest.raises(HTTPException) as exc_info:
            service.authenticate_user("superadmin@test.com", "wrongpass")
        
        assert exc_info.value.status_code == 401
    
    def test_authenticate_user_nonexistent(self, db):
        """Test authentication with nonexistent user"""
        service = AuthService(db)
        
        with pytest.raises(HTTPException) as exc_info:
            service.authenticate_user("nonexistent@test.com", "password")
        
        assert exc_info.value.status_code == 401
    
    def test_create_token_for_user(self, db, superadmin_user):
        """Test creating token for user"""
        service = AuthService(db)
        
        token = service.create_token_for_user(superadmin_user)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0


class TestUserService:
    """Test UserService"""
    
    def test_get_all_users(self, db, superadmin_user, admin_user):
        """Test getting all users"""
        service = UserService(db)
        
        users = service.get_all_users()
        
        assert len(users) >= 2
    
    def test_get_user_by_id(self, db, superadmin_user):
        """Test getting user by ID"""
        service = UserService(db)
        
        user = service.get_user_by_id(superadmin_user.id)
        
        assert user.id == superadmin_user.id
        assert user.email == superadmin_user.email
    
    def test_get_user_by_id_not_found(self, db):
        """Test getting nonexistent user"""
        service = UserService(db)
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_user_by_id(9999)
        
        assert exc_info.value.status_code == 404
    
    def test_create_user(self, db):
        """Test creating a new user"""
        service = UserService(db)
        user_data = UserCreate(
            email="newuser@test.com",
            password="password123",
            name="New User",
            role=RoleEnum.user
        )
        
        user = service.create_user(user_data)
        
        assert user.id is not None
        assert user.email == "newuser@test.com"
        assert user.name == "New User"
    
    def test_create_user_duplicate_email(self, db, superadmin_user):
        """Test creating user with duplicate email"""
        service = UserService(db)
        user_data = UserCreate(
            email=superadmin_user.email,
            password="password123",
            name="Duplicate"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_user(user_data)
        
        assert exc_info.value.status_code == 400
    
    def test_update_user(self, db, superadmin_user):
        """Test updating a user"""
        service = UserService(db)
        update_data = UserUpdate(name="Updated Name")
        
        updated = service.update_user(superadmin_user.id, update_data)
        
        assert updated.name == "Updated Name"
    
    def test_delete_user(self, db, admin_user):
        """Test deleting a user"""
        service = UserService(db)
        
        result = service.delete_user(admin_user.id)
        
        assert result is True
        with pytest.raises(HTTPException):
            service.get_user_by_id(admin_user.id)


class TestCompanyService:
    """Test CompanyService"""
    
    def test_get_all_companies(self, db, test_company):
        """Test getting all companies"""
        service = CompanyService(db)
        
        companies = service.get_all_companies()
        
        assert len(companies) >= 1
    
    def test_get_company_by_id(self, db, test_company):
        """Test getting company by ID"""
        service = CompanyService(db)
        
        company = service.get_company_by_id(test_company.id)
        
        assert company.id == test_company.id
        assert company.name == test_company.name
    
    def test_create_company(self, db):
        """Test creating a new company"""
        service = CompanyService(db)
        company_data = CompanyCreate(
            name="New Company",
            cnpj="98.765.432/0001-10",
            email="new@company.com"
        )
        
        company = service.create_company(company_data)
        
        assert company.id is not None
        assert company.name == "New Company"
        assert company.cnpj == "98.765.432/0001-10"
    
    def test_create_company_duplicate_cnpj(self, db, test_company):
        """Test creating company with duplicate CNPJ"""
        service = CompanyService(db)
        company_data = CompanyCreate(
            name="Duplicate",
            cnpj=test_company.cnpj
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_company(company_data)
        
        assert exc_info.value.status_code == 400
    
    def test_update_company(self, db, test_company):
        """Test updating a company"""
        service = CompanyService(db)
        update_data = CompanyUpdate(name="Updated Company")
        
        updated = service.update_company(test_company.id, update_data)
        
        assert updated.name == "Updated Company"


class TestInvoiceService:
    """Test InvoiceService"""
    
    def test_get_all_invoices(self, db, test_company, superadmin_user):
        """Test getting all invoices"""
        # Create a test invoice
        invoice = Invoice(
            company_id=test_company.id,
            description="Test",
            amount=1000,
            due_date=date.today(),
            created_by=superadmin_user.id
        )
        db.add(invoice)
        db.commit()
        
        service = InvoiceService(db)
        invoices = service.get_all_invoices()
        
        assert len(invoices) >= 1
    
    def test_get_invoice_by_id(self, db, test_company, superadmin_user):
        """Test getting invoice by ID"""
        invoice = Invoice(
            company_id=test_company.id,
            description="Test",
            amount=1000,
            due_date=date.today(),
            created_by=superadmin_user.id
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        service = InvoiceService(db)
        found = service.get_invoice_by_id(invoice.id)
        
        assert found.id == invoice.id
    
    def test_create_invoice(self, db, test_company, superadmin_user):
        """Test creating a new invoice"""
        service = InvoiceService(db)
        invoice_data = InvoiceCreate(
            company_id=test_company.id,
            description="New Invoice",
            amount=1500.00,
            due_date=date.today() + timedelta(days=30)
        )
        
        invoice = service.create_invoice(invoice_data, superadmin_user.id)
        
        assert invoice.id is not None
        assert invoice.description == "New Invoice"
        assert float(invoice.amount) == 1500.00
    
    def test_update_invoice(self, db, test_company, superadmin_user):
        """Test updating an invoice"""
        invoice = Invoice(
            company_id=test_company.id,
            description="Test",
            amount=1000,
            due_date=date.today(),
            created_by=superadmin_user.id
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        service = InvoiceService(db)
        update_data = InvoiceUpdate(description="Updated Invoice")
        updated = service.update_invoice(invoice.id, update_data)
        
        assert updated.description == "Updated Invoice"
    
    def test_toggle_paid_status(self, db, test_company, superadmin_user):
        """Test toggling paid status"""
        invoice = Invoice(
            company_id=test_company.id,
            description="Test",
            amount=1000,
            due_date=date.today(),
            is_paid=False,
            created_by=superadmin_user.id
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        service = InvoiceService(db)
        updated = service.toggle_paid_status(invoice.id)
        
        assert updated.is_paid is True
        assert updated.paid_at is not None
    
    def test_get_dashboard_stats(self, db, test_company, superadmin_user):
        """Test getting dashboard stats"""
        # Create test invoices
        paid = Invoice(
            company_id=test_company.id,
            description="Paid",
            amount=1000,
            due_date=date.today(),
            is_paid=True,
            created_by=superadmin_user.id
        )
        unpaid = Invoice(
            company_id=test_company.id,
            description="Unpaid",
            amount=2000,
            due_date=date.today() + timedelta(days=5),
            is_paid=False,
            created_by=superadmin_user.id
        )
        db.add_all([paid, unpaid])
        db.commit()
        
        service = InvoiceService(db)
        stats = service.get_dashboard_stats()
        
        assert stats["total"] >= 2
        assert stats["paid"] >= 1
        assert stats["pending"] >= 1
        assert "pending_amount" in stats
