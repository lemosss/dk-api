import pytest
from app.repositories.user_repository import UserRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.invoice_repository import InvoiceRepository
from app.models import User, Company, Invoice, RoleEnum
from app.core.security import get_password_hash
from datetime import date, timedelta


class TestEdgeCases:
    """Test edge cases and additional scenarios"""
    
    def test_user_repo_get_active_users(self, db):
        """Test getting only active users"""
        repo = UserRepository(db)
        
        active = User(
            email="active@test.com",
            hashed_password=get_password_hash("test"),
            role=RoleEnum.user,
            is_active=True
        )
        inactive = User(
            email="inactive@test.com",
            hashed_password=get_password_hash("test"),
            role=RoleEnum.user,
            is_active=False
        )
        repo.create(active)
        repo.create(inactive)
        
        active_users = repo.get_active_users()
        
        assert len(active_users) >= 1
        for user in active_users:
            assert user.is_active is True
    
    def test_user_repo_get_by_company(self, db, test_company):
        """Test getting users by company"""
        repo = UserRepository(db)
        
        user1 = User(
            email="user1@test.com",
            hashed_password=get_password_hash("test"),
            role=RoleEnum.user,
            company_id=test_company.id
        )
        user2 = User(
            email="user2@test.com",
            hashed_password=get_password_hash("test"),
            role=RoleEnum.user,
            company_id=test_company.id
        )
        repo.create(user1)
        repo.create(user2)
        
        company_users = repo.get_by_company(test_company.id)
        
        assert len(company_users) >= 2
    
    def test_base_repo_delete_nonexistent(self, db):
        """Test deleting nonexistent record"""
        repo = UserRepository(db)
        
        result = repo.delete(9999)
        
        assert result is False
    
    def test_invoice_repo_get_unpaid_invoices(self, db, test_company, superadmin_user):
        """Test getting unpaid invoices"""
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
        
        unpaid_invoices = repo.get_unpaid_invoices()
        
        assert len(unpaid_invoices) >= 1
        for inv in unpaid_invoices:
            assert inv.is_paid is False
    
    def test_invoice_service_update_mark_as_paid(self, db, test_company, superadmin_user):
        """Test updating invoice to mark as paid"""
        from app.services.invoice_service import InvoiceService
        from app.schemas.invoice import InvoiceUpdate
        
        service = InvoiceService(db)
        
        # Create unpaid invoice
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
        
        # Mark as paid
        update_data = InvoiceUpdate(is_paid=True)
        updated = service.update_invoice(invoice.id, update_data)
        
        assert updated.is_paid is True
        assert updated.paid_at is not None
    
    def test_invoice_service_update_unmark_as_paid(self, db, test_company, superadmin_user):
        """Test updating invoice to unmark as paid"""
        from app.services.invoice_service import InvoiceService
        from app.schemas.invoice import InvoiceUpdate
        from datetime import datetime
        
        service = InvoiceService(db)
        
        # Create paid invoice
        invoice = Invoice(
            company_id=test_company.id,
            description="Test",
            amount=1000,
            due_date=date.today(),
            is_paid=True,
            paid_at=datetime.utcnow(),
            created_by=superadmin_user.id
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        # Unmark as paid
        update_data = InvoiceUpdate(is_paid=False)
        updated = service.update_invoice(invoice.id, update_data)
        
        assert updated.is_paid is False
        assert updated.paid_at is None
    
    def test_invoice_service_calendar_data_empty_month(self, db):
        """Test getting calendar data for a month with no invoices"""
        from app.services.invoice_service import InvoiceService
        
        service = InvoiceService(db)
        
        # Get calendar for future month with no invoices
        calendar_data = service.get_calendar_data(12, 2099)
        
        assert calendar_data["month"] == 12
        assert calendar_data["year"] == 2099
        assert calendar_data["days"] == {}
    
    def test_company_service_update_company_duplicate_cnpj(self, db):
        """Test updating company with duplicate CNPJ"""
        from app.services.company_service import CompanyService
        from app.schemas.company import CompanyCreate, CompanyUpdate
        
        service = CompanyService(db)
        
        # Create two companies
        company1 = service.create_company(CompanyCreate(
            name="Company 1",
            cnpj="11.111.111/0001-11"
        ))
        company2 = service.create_company(CompanyCreate(
            name="Company 2",
            cnpj="22.222.222/0001-22"
        ))
        
        # Try to update company2 with company1's CNPJ
        with pytest.raises(Exception):  # HTTPException
            service.update_company(company2.id, CompanyUpdate(cnpj=company1.cnpj))
    
    def test_user_service_update_user_duplicate_email(self, db, admin_user, superadmin_user):
        """Test updating user with duplicate email"""
        from app.services.user_service import UserService
        from app.schemas.user import UserUpdate
        
        service = UserService(db)
        
        # Try to update admin with superadmin's email
        with pytest.raises(Exception):  # HTTPException
            service.update_user(admin_user.id, UserUpdate(email=superadmin_user.email))
