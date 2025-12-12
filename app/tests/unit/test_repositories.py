import pytest
from datetime import date, timedelta
from app.repositories.user_repository import UserRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.invoice_repository import InvoiceRepository
from app.models import User, Company, Invoice, RoleEnum
from app.core.security import get_password_hash


class TestUserRepository:
    """Test UserRepository"""
    
    def test_create_user(self, db):
        """Test creating a user"""
        repo = UserRepository(db)
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("test123"),
            name="Test User",
            role=RoleEnum.user
        )
        created = repo.create(user)
        
        assert created.id is not None
        assert created.email == "test@example.com"
        assert created.name == "Test User"
    
    def test_get_user_by_id(self, db):
        """Test getting user by ID"""
        repo = UserRepository(db)
        user = User(email="test@example.com", hashed_password="hash", role=RoleEnum.user)
        created = repo.create(user)
        
        found = repo.get(created.id)
        
        assert found is not None
        assert found.id == created.id
        assert found.email == created.email
    
    def test_get_user_by_email(self, db):
        """Test getting user by email"""
        repo = UserRepository(db)
        user = User(email="test@example.com", hashed_password="hash", role=RoleEnum.user)
        repo.create(user)
        
        found = repo.get_by_email("test@example.com")
        
        assert found is not None
        assert found.email == "test@example.com"
    
    def test_get_user_by_role(self, db):
        """Test getting users by role"""
        repo = UserRepository(db)
        user1 = User(email="admin@example.com", hashed_password="hash", role=RoleEnum.admin)
        user2 = User(email="user@example.com", hashed_password="hash", role=RoleEnum.user)
        repo.create(user1)
        repo.create(user2)
        
        admins = repo.get_by_role(RoleEnum.admin)
        
        assert len(admins) == 1
        assert admins[0].role == RoleEnum.admin
    
    def test_update_user(self, db):
        """Test updating a user"""
        repo = UserRepository(db)
        user = User(email="test@example.com", hashed_password="hash", role=RoleEnum.user)
        created = repo.create(user)
        
        updated = repo.update(created, {"name": "Updated Name"})
        
        assert updated.name == "Updated Name"
    
    def test_delete_user(self, db):
        """Test deleting a user"""
        repo = UserRepository(db)
        user = User(email="test@example.com", hashed_password="hash", role=RoleEnum.user)
        created = repo.create(user)
        
        result = repo.delete(created.id)
        
        assert result is True
        assert repo.get(created.id) is None


class TestCompanyRepository:
    """Test CompanyRepository"""
    
    def test_create_company(self, db):
        """Test creating a company"""
        repo = CompanyRepository(db)
        company = Company(
            name="Test Company",
            cnpj="12.345.678/0001-90",
            email="test@company.com"
        )
        created = repo.create(company)
        
        assert created.id is not None
        assert created.name == "Test Company"
        assert created.cnpj == "12.345.678/0001-90"
    
    def test_get_company_by_cnpj(self, db):
        """Test getting company by CNPJ"""
        repo = CompanyRepository(db)
        company = Company(name="Test", cnpj="12.345.678/0001-90")
        repo.create(company)
        
        found = repo.get_by_cnpj("12.345.678/0001-90")
        
        assert found is not None
        assert found.cnpj == "12.345.678/0001-90"
    
    def test_get_active_companies(self, db):
        """Test getting active companies"""
        repo = CompanyRepository(db)
        active = Company(name="Active", cnpj="12.345.678/0001-90", is_active=True)
        inactive = Company(name="Inactive", cnpj="98.765.432/0001-10", is_active=False)
        repo.create(active)
        repo.create(inactive)
        
        active_companies = repo.get_active_companies()
        
        assert len(active_companies) == 1
        assert active_companies[0].is_active is True


class TestInvoiceRepository:
    """Test InvoiceRepository"""
    
    def test_create_invoice(self, db, test_company, superadmin_user):
        """Test creating an invoice"""
        repo = InvoiceRepository(db)
        invoice = Invoice(
            company_id=test_company.id,
            description="Test Invoice",
            amount=1000.00,
            due_date=date.today(),
            created_by=superadmin_user.id
        )
        created = repo.create(invoice)
        
        assert created.id is not None
        assert created.description == "Test Invoice"
        assert float(created.amount) == 1000.00
    
    def test_get_by_company(self, db, test_company, superadmin_user):
        """Test getting invoices by company"""
        repo = InvoiceRepository(db)
        invoice = Invoice(
            company_id=test_company.id,
            description="Test",
            amount=1000,
            due_date=date.today(),
            created_by=superadmin_user.id
        )
        repo.create(invoice)
        
        invoices = repo.get_by_company(test_company.id)
        
        assert len(invoices) == 1
        assert invoices[0].company_id == test_company.id
    
    def test_get_paid_invoices(self, db, test_company, superadmin_user):
        """Test getting paid invoices"""
        repo = InvoiceRepository(db)
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
            due_date=date.today(),
            is_paid=False,
            created_by=superadmin_user.id
        )
        repo.create(paid)
        repo.create(unpaid)
        
        paid_invoices = repo.get_paid_invoices()
        
        assert len(paid_invoices) == 1
        assert paid_invoices[0].is_paid is True
    
    def test_get_overdue_invoices(self, db, test_company, superadmin_user):
        """Test getting overdue invoices"""
        repo = InvoiceRepository(db)
        overdue = Invoice(
            company_id=test_company.id,
            description="Overdue",
            amount=1000,
            due_date=date.today() - timedelta(days=10),
            is_paid=False,
            created_by=superadmin_user.id
        )
        current = Invoice(
            company_id=test_company.id,
            description="Current",
            amount=2000,
            due_date=date.today() + timedelta(days=10),
            is_paid=False,
            created_by=superadmin_user.id
        )
        repo.create(overdue)
        repo.create(current)
        
        overdue_invoices = repo.get_overdue_invoices()
        
        assert len(overdue_invoices) == 1
        assert overdue_invoices[0].description == "Overdue"
    
    def test_get_by_month_year(self, db, test_company, superadmin_user):
        """Test getting invoices by month and year"""
        repo = InvoiceRepository(db)
        today = date.today()
        invoice = Invoice(
            company_id=test_company.id,
            description="Test",
            amount=1000,
            due_date=today,
            created_by=superadmin_user.id
        )
        repo.create(invoice)
        
        invoices = repo.get_by_month_year(today.month, today.year)
        
        assert len(invoices) >= 1
