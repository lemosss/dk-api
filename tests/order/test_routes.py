import pytest
from datetime import date, timedelta
from io import BytesIO


class TestCompanyRoutes:
    """Test company routes"""
    
    def test_list_companies_as_admin(self, client, admin_token, test_company):
        """Test listing companies as admin"""
        response = client.get(
            "/api/companies/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        companies = response.json()
        assert len(companies) >= 1
    
    def test_list_companies_as_user(self, client, user_token, test_company):
        """Test listing companies as user (should only see own company)"""
        response = client.get(
            "/api/companies/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        companies = response.json()
        assert len(companies) == 1
        assert companies[0]["id"] == test_company.id
    
    def test_get_company_as_admin(self, client, admin_token, test_company):
        """Test getting company as admin"""
        response = client.get(
            f"/api/companies/{test_company.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_company.id
    
    def test_get_company_as_user_own_company(self, client, user_token, test_company):
        """Test getting own company as user"""
        response = client.get(
            f"/api/companies/{test_company.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
    
    def test_get_company_as_user_other_company(self, client, user_token, db_session):
        """Test getting other company as user (should fail)"""
        from app.order.models import Company
        
        # Create another company
        other_company = Company(name="Other", cnpj="99.999.999/0001-99")
        db_session.add(other_company)
        db_session.commit()
        
        response = client.get(
            f"/api/companies/{other_company.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 403
    
    def test_create_company_as_admin(self, client, admin_token):
        """Test creating company as admin"""
        company_data = {
            "name": "New Company",
            "cnpj": "11.222.333/0001-44",
            "email": "new@company.com"
        }
        
        response = client.post(
            "/api/companies/",
            json=company_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Company"
    
    def test_create_company_as_user(self, client, user_token):
        """Test creating company as user (should fail)"""
        company_data = {
            "name": "Test",
            "cnpj": "11.222.333/0001-55"
        }
        
        response = client.post(
            "/api/companies/",
            json=company_data,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 403
    
    def test_update_company_as_admin(self, client, admin_token, test_company):
        """Test updating company as admin"""
        update_data = {
            "name": "Updated Company"
        }
        
        response = client.put(
            f"/api/companies/{test_company.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Company"
    
    def test_delete_company_as_superadmin(self, client, superadmin_token, test_company):
        """Test deleting company as superadmin"""
        response = client.delete(
            f"/api/companies/{test_company.id}",
            headers={"Authorization": f"Bearer {superadmin_token}"}
        )
        
        assert response.status_code == 200
    
    def test_delete_company_as_admin(self, client, admin_token, test_company):
        """Test deleting company as admin (should fail)"""
        response = client.delete(
            f"/api/companies/{test_company.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 403


class TestInvoiceRoutes:
    """Test invoice routes"""
    
    def test_list_invoices_as_admin(self, client, admin_token, test_invoice):
        """Test listing invoices as admin"""
        response = client.get(
            "/api/invoices/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        invoices = response.json()
        assert len(invoices) >= 1
    
    def test_list_invoices_as_user(self, client, user_token, test_invoice):
        """Test listing invoices as user"""
        response = client.get(
            "/api/invoices/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        invoices = response.json()
        # Should only see invoices for own company
        for inv in invoices:
            assert inv["company_id"] == test_invoice.company_id
    
    def test_list_invoices_with_filters(self, client, admin_token, test_invoice):
        """Test listing invoices with filters"""
        today = date.today()
        response = client.get(
            f"/api/invoices/?month={today.month}&year={today.year}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
    
    def test_get_invoice_by_id(self, client, admin_token, test_invoice):
        """Test getting invoice by ID"""
        response = client.get(
            f"/api/invoices/{test_invoice.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_invoice.id
    
    def test_get_invoice_as_user_own_company(self, client, user_token, test_invoice):
        """Test getting invoice from own company as user"""
        response = client.get(
            f"/api/invoices/{test_invoice.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
    
    def test_create_invoice_as_admin(self, client, admin_token, test_company):
        """Test creating invoice as admin"""
        invoice_data = {
            "company_id": test_company.id,
            "description": "New Invoice",
            "amount": 1500.00,
            "due_date": str(date.today() + timedelta(days=10))
        }
        
        response = client.post(
            "/api/invoices/",
            json=invoice_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "New Invoice"
        assert float(data["amount"]) == 1500.00
    
    def test_create_invoice_as_user(self, client, user_token, test_company):
        """Test creating invoice as user (should fail)"""
        invoice_data = {
            "company_id": test_company.id,
            "description": "Test",
            "amount": 100.00,
            "due_date": str(date.today())
        }
        
        response = client.post(
            "/api/invoices/",
            json=invoice_data,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 403
    
    def test_update_invoice_as_admin(self, client, admin_token, test_invoice):
        """Test updating invoice as admin"""
        update_data = {
            "description": "Updated Invoice"
        }
        
        response = client.put(
            f"/api/invoices/{test_invoice.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated Invoice"
    
    def test_toggle_invoice_paid(self, client, admin_token, test_invoice):
        """Test toggling invoice paid status"""
        original_status = test_invoice.is_paid
        
        response = client.patch(
            f"/api/invoices/{test_invoice.id}/toggle-paid",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_paid"] != original_status
    
    def test_delete_invoice_as_admin(self, client, admin_token, test_invoice):
        """Test deleting invoice as admin"""
        response = client.delete(
            f"/api/invoices/{test_invoice.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
    
    def test_delete_invoice_as_user(self, client, user_token, test_invoice):
        """Test deleting invoice as user (should fail)"""
        response = client.delete(
            f"/api/invoices/{test_invoice.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 403
    
    def test_get_invoices_by_date(self, client, admin_token, test_invoice):
        """Test getting invoices by specific date"""
        target_date = test_invoice.due_date.strftime("%Y-%m-%d")
        
        response = client.get(
            f"/api/invoices/by-date?date={target_date}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        invoices = response.json()
        assert isinstance(invoices, list)
    
    def test_get_invoices_by_date_invalid_format(self, client, admin_token):
        """Test getting invoices by date with invalid format"""
        response = client.get(
            "/api/invoices/by-date?date=invalid-date",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 400


class TestInvoiceFileUpload:
    """Test invoice file upload functionality"""
    
    def test_upload_invoice_file_as_admin(self, client, admin_token, test_invoice):
        """Test uploading PDF file for invoice as admin"""
        # Create a mock PDF file
        pdf_content = b"%PDF-1.4 mock pdf content"
        files = {"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")}
        
        response = client.post(
            f"/api/invoices/{test_invoice.id}/upload",
            files=files,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "file_url" in data
    
    def test_upload_invoice_file_wrong_type(self, client, admin_token, test_invoice):
        """Test uploading non-PDF file (should fail)"""
        files = {"file": ("test.txt", BytesIO(b"text content"), "text/plain")}
        
        response = client.post(
            f"/api/invoices/{test_invoice.id}/upload",
            files=files,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 400
    
    def test_upload_invoice_file_as_user(self, client, user_token, test_invoice):
        """Test uploading file as user (should fail)"""
        pdf_content = b"%PDF-1.4 mock pdf"
        files = {"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")}
        
        response = client.post(
            f"/api/invoices/{test_invoice.id}/upload",
            files=files,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 403
    
    def test_delete_invoice_file_as_admin(self, client, admin_token, test_invoice):
        """Test deleting invoice file as admin"""
        response = client.delete(
            f"/api/invoices/{test_invoice.id}/file",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["ok"] is True
