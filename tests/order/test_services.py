import pytest
from fastapi import HTTPException
from datetime import date, timedelta
from app.order.models import Company, Invoice
from app.order.schemas import CompanyCreate, CompanyUpdate, InvoiceCreate, InvoiceUpdate
from app.order import services
from app.user.models import RoleEnum


class TestCompanyServices:
    """Test company services"""
    
    def test_get_company_by_id_exists(self, db_session, test_company):
        """Test getting existing company by ID"""
        company = services.get_company_by_id(db_session, test_company.id)
        
        assert company is not None
        assert company.id == test_company.id
        assert company.name == test_company.name
    
    def test_get_company_by_id_not_exists(self, db_session):
        """Test getting nonexistent company by ID"""
        with pytest.raises(HTTPException) as exc_info:
            services.get_company_by_id(db_session, 99999)
        
        assert exc_info.value.status_code == 404
    
    def test_get_company_by_cnpj_exists(self, db_session, test_company):
        """Test getting existing company by CNPJ"""
        company = services.get_company_by_cnpj(db_session, test_company.cnpj)
        
        assert company is not None
        assert company.cnpj == test_company.cnpj
    
    def test_get_company_by_cnpj_not_exists(self, db_session):
        """Test getting nonexistent company by CNPJ"""
        company = services.get_company_by_cnpj(db_session, "99.999.999/0001-99")
        
        assert company is None
    
    def test_get_all_companies(self, db_session, test_company):
        """Test getting all companies"""
        companies = services.get_all_companies(db_session)
        
        assert len(companies) >= 1
        assert test_company.id in [c.id for c in companies]
    
    def test_get_user_companies_as_admin(self, db_session, test_admin, test_company):
        """Test getting companies as admin (should get all)"""
        companies = services.get_user_companies(db_session, test_admin)
        
        assert len(companies) >= 1
    
    def test_get_user_companies_as_user(self, db_session, test_user, test_company):
        """Test getting companies as regular user (should get only own)"""
        companies = services.get_user_companies(db_session, test_user)
        
        assert len(companies) == 1
        assert companies[0].id == test_company.id
    
    def test_create_new_company(self, db_session):
        """Test creating new company"""
        company_data = CompanyCreate(
            name="New Company",
            cnpj="98.765.432/0001-10",
            email="new@company.com",
            phone="(11) 9876-5432"
        )
        
        company = services.create_new_company(db_session, company_data)
        
        assert company is not None
        assert company.name == "New Company"
        assert company.cnpj == "98.765.432/0001-10"
    
    def test_create_new_company_duplicate_cnpj(self, db_session, test_company):
        """Test creating company with duplicate CNPJ"""
        company_data = CompanyCreate(
            name="Duplicate",
            cnpj=test_company.cnpj
        )
        
        with pytest.raises(HTTPException) as exc_info:
            services.create_new_company(db_session, company_data)
        
        assert exc_info.value.status_code == 400
    
    def test_update_company_data(self, db_session, test_company):
        """Test updating company data"""
        update_data = CompanyUpdate(
            name="Updated Company Name",
            email="updated@company.com"
        )
        
        company = services.update_company_data(db_session, test_company.id, update_data)
        
        assert company.name == "Updated Company Name"
        assert company.email == "updated@company.com"
    
    def test_delete_company_by_id(self, db_session, test_company):
        """Test deleting company"""
        company_id = test_company.id
        services.delete_company_by_id(db_session, company_id)
        
        company = db_session.query(Company).filter(Company.id == company_id).first()
        assert company is None


class TestInvoiceServices:
    """Test invoice services"""
    
    def test_get_invoice_by_id_exists(self, db_session, test_invoice):
        """Test getting existing invoice by ID"""
        invoice = services.get_invoice_by_id(db_session, test_invoice.id)
        
        assert invoice is not None
        assert invoice.id == test_invoice.id
    
    def test_get_invoice_by_id_not_exists(self, db_session):
        """Test getting nonexistent invoice by ID"""
        with pytest.raises(HTTPException) as exc_info:
            services.get_invoice_by_id(db_session, 99999)
        
        assert exc_info.value.status_code == 404
    
    def test_get_all_invoices_as_admin(self, db_session, test_admin, test_invoice):
        """Test getting all invoices as admin"""
        results = services.get_all_invoices(db_session, test_admin)
        
        assert len(results) >= 1
    
    def test_get_all_invoices_as_user(self, db_session, test_user, test_invoice):
        """Test getting invoices as user (filtered by company)"""
        results = services.get_all_invoices(db_session, test_user)
        
        # Should only get invoices for user's company
        for inv, company_name in results:
            assert inv.company_id == test_user.company_id
    
    def test_get_all_invoices_with_filters(self, db_session, test_admin, test_invoice):
        """Test getting invoices with filters"""
        today = date.today()
        results = services.get_all_invoices(
            db_session, 
            test_admin, 
            month=today.month, 
            year=today.year
        )
        
        # All results should be in the specified month/year
        for inv, company_name in results:
            assert inv.due_date.month == today.month or inv.due_date.year == today.year
    
    def test_create_new_invoice(self, db_session, test_company, test_admin):
        """Test creating new invoice"""
        invoice_data = InvoiceCreate(
            company_id=test_company.id,
            description="Test Invoice",
            amount=2500.00,
            due_date=date.today() + timedelta(days=15)
        )
        
        invoice = services.create_new_invoice(db_session, invoice_data, test_admin.id)
        
        assert invoice is not None
        assert invoice.description == "Test Invoice"
        assert invoice.amount == 2500.00
        assert invoice.created_by == test_admin.id
    
    def test_update_invoice_data(self, db_session, test_invoice):
        """Test updating invoice data"""
        update_data = InvoiceUpdate(
            description="Updated Description",
            amount=3000.00
        )
        
        invoice = services.update_invoice_data(db_session, test_invoice.id, update_data)
        
        assert invoice.description == "Updated Description"
        assert invoice.amount == 3000.00
    
    def test_update_invoice_mark_as_paid(self, db_session, test_invoice):
        """Test marking invoice as paid"""
        assert test_invoice.is_paid is False
        assert test_invoice.paid_at is None
        
        update_data = InvoiceUpdate(is_paid=True)
        invoice = services.update_invoice_data(db_session, test_invoice.id, update_data)
        
        assert invoice.is_paid is True
        assert invoice.paid_at is not None
    
    def test_update_invoice_mark_as_unpaid(self, db_session, test_invoice):
        """Test marking invoice as unpaid"""
        # First mark as paid
        update_data = InvoiceUpdate(is_paid=True)
        services.update_invoice_data(db_session, test_invoice.id, update_data)
        
        # Then mark as unpaid
        update_data = InvoiceUpdate(is_paid=False)
        invoice = services.update_invoice_data(db_session, test_invoice.id, update_data)
        
        assert invoice.is_paid is False
        assert invoice.paid_at is None
    
    def test_toggle_invoice_paid(self, db_session, test_invoice):
        """Test toggling invoice paid status"""
        original_status = test_invoice.is_paid
        
        invoice = services.toggle_invoice_paid(db_session, test_invoice.id)
        
        assert invoice.is_paid != original_status
    
    def test_delete_invoice_by_id(self, db_session, test_invoice):
        """Test deleting invoice"""
        invoice_id = test_invoice.id
        services.delete_invoice_by_id(db_session, invoice_id)
        
        invoice = db_session.query(Invoice).filter(Invoice.id == invoice_id).first()
        assert invoice is None
    
    def test_check_invoice_access_allowed(self, test_user, test_invoice):
        """Test checking invoice access when allowed"""
        # Should not raise exception
        services.check_invoice_access(test_user, test_invoice)
    
    def test_check_invoice_access_denied(self, test_user, test_invoice, db_session):
        """Test checking invoice access when denied"""
        # Change invoice company to different company
        test_invoice.company_id = 99999
        db_session.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            services.check_invoice_access(test_user, test_invoice)
        
        assert exc_info.value.status_code == 403
    
    def test_check_company_access_allowed(self, test_user, test_company):
        """Test checking company access when allowed"""
        # Should not raise exception
        services.check_company_access(test_user, test_company.id)
    
    def test_check_company_access_denied(self, test_user):
        """Test checking company access when denied"""
        with pytest.raises(HTTPException) as exc_info:
            services.check_company_access(test_user, 99999)
        
        assert exc_info.value.status_code == 403
