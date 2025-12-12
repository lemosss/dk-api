import pytest
from datetime import date
from pydantic import ValidationError
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyOut
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceOut
from app.schemas.token import Token, TokenData
from app.models import RoleEnum


class TestUserSchemas:
    """Test User schemas"""
    
    def test_user_create_valid(self):
        """Test creating valid UserCreate schema"""
        data = {
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User",
            "role": RoleEnum.user
        }
        user = UserCreate(**data)
        
        assert user.email == "test@example.com"
        assert user.password == "password123"
        assert user.name == "Test User"
        assert user.role == RoleEnum.user
    
    def test_user_create_invalid_email(self):
        """Test UserCreate with invalid email"""
        data = {
            "email": "invalid-email",
            "password": "password123"
        }
        
        with pytest.raises(ValidationError):
            UserCreate(**data)
    
    def test_user_create_defaults(self):
        """Test UserCreate default values"""
        data = {
            "email": "test@example.com",
            "password": "password123"
        }
        user = UserCreate(**data)
        
        assert user.role == RoleEnum.user
        assert user.name is None
        assert user.company_id is None
    
    def test_user_update_partial(self):
        """Test UserUpdate with partial data"""
        data = {"name": "Updated Name"}
        user = UserUpdate(**data)
        
        assert user.name == "Updated Name"
        assert user.email is None


class TestCompanySchemas:
    """Test Company schemas"""
    
    def test_company_create_valid(self):
        """Test creating valid CompanyCreate schema"""
        data = {
            "name": "Test Company",
            "cnpj": "12.345.678/0001-90",
            "email": "test@company.com",
            "phone": "(11) 1234-5678"
        }
        company = CompanyCreate(**data)
        
        assert company.name == "Test Company"
        assert company.cnpj == "12.345.678/0001-90"
        assert company.email == "test@company.com"
    
    def test_company_create_minimal(self):
        """Test CompanyCreate with minimal required fields"""
        data = {
            "name": "Test Company",
            "cnpj": "12.345.678/0001-90"
        }
        company = CompanyCreate(**data)
        
        assert company.name == "Test Company"
        assert company.cnpj == "12.345.678/0001-90"
        assert company.email is None
    
    def test_company_update_partial(self):
        """Test CompanyUpdate with partial data"""
        data = {"name": "Updated Company"}
        company = CompanyUpdate(**data)
        
        assert company.name == "Updated Company"
        assert company.cnpj is None


class TestInvoiceSchemas:
    """Test Invoice schemas"""
    
    def test_invoice_create_valid(self):
        """Test creating valid InvoiceCreate schema"""
        data = {
            "company_id": 1,
            "description": "Test Invoice",
            "amount": 1000.00,
            "due_date": date.today(),
            "notes": "Test notes"
        }
        invoice = InvoiceCreate(**data)
        
        assert invoice.company_id == 1
        assert invoice.description == "Test Invoice"
        assert invoice.amount == 1000.00
        assert invoice.due_date == date.today()
    
    def test_invoice_create_minimal(self):
        """Test InvoiceCreate with minimal fields"""
        data = {
            "company_id": 1,
            "description": "Test",
            "amount": 100.00,
            "due_date": date.today()
        }
        invoice = InvoiceCreate(**data)
        
        assert invoice.notes is None
        assert invoice.file_url is None
    
    def test_invoice_update_partial(self):
        """Test InvoiceUpdate with partial data"""
        data = {"is_paid": True}
        invoice = InvoiceUpdate(**data)
        
        assert invoice.is_paid is True
        assert invoice.description is None


class TestTokenSchemas:
    """Test Token schemas"""
    
    def test_token_valid(self):
        """Test creating valid Token schema"""
        data = {
            "access_token": "test.token.here",
            "token_type": "bearer"
        }
        token = Token(**data)
        
        assert token.access_token == "test.token.here"
        assert token.token_type == "bearer"
    
    def test_token_default_type(self):
        """Test Token with default token_type"""
        data = {"access_token": "test.token.here"}
        token = Token(**data)
        
        assert token.token_type == "bearer"
    
    def test_token_data(self):
        """Test TokenData schema"""
        data = {"user_id": 123, "role": "admin"}
        token_data = TokenData(**data)
        
        assert token_data.user_id == 123
        assert token_data.role == "admin"
