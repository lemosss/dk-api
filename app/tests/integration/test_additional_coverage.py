import pytest


class TestAdditionalEndpointCoverage:
    """Additional tests to improve endpoint coverage"""
    
    def test_list_companies_user_without_company(self, client, db):
        """Test listing companies as user without a company"""
        from app.models import User, RoleEnum
        from app.core.security import get_password_hash
        
        # Create user without company
        user = User(
            email="nocompany@test.com",
            hashed_password=get_password_hash("test123"),
            role=RoleEnum.user,
            company_id=None,
            is_active=True
        )
        db.add(user)
        db.commit()
        
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "nocompany@test.com", "password": "test123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # List companies (should return empty list)
        response = client.get("/api/v1/companies/", headers=headers)
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_invoice_not_found(self, client, auth_headers_admin):
        """Test getting nonexistent invoice"""
        response = client.get("/api/v1/invoices/9999", headers=auth_headers_admin)
        
        assert response.status_code == 404
    
    def test_upload_invoice_not_found(self, client, auth_headers_admin):
        """Test uploading file to nonexistent invoice"""
        from io import BytesIO
        
        files = {"file": ("test.pdf", BytesIO(b"%PDF-1.4"), "application/pdf")}
        
        response = client.post(
            "/api/v1/invoices/9999/upload",
            files=files,
            headers=auth_headers_admin
        )
        
        assert response.status_code == 404
    
    def test_update_invoice_not_found(self, client, auth_headers_admin):
        """Test updating nonexistent invoice"""
        response = client.put(
            "/api/v1/invoices/9999",
            json={"description": "Test"},
            headers=auth_headers_admin
        )
        
        assert response.status_code == 404
    
    def test_toggle_paid_invoice_not_found(self, client, auth_headers_admin):
        """Test toggling paid status on nonexistent invoice"""
        response = client.patch(
            "/api/v1/invoices/9999/toggle-paid",
            headers=auth_headers_admin
        )
        
        assert response.status_code == 404
    
    def test_delete_invoice_not_found(self, client, auth_headers_admin):
        """Test deleting nonexistent invoice"""
        response = client.delete("/api/v1/invoices/9999", headers=auth_headers_admin)
        
        assert response.status_code == 404
    
    def test_get_invoices_by_date_invalid_format(self, client, auth_headers_admin):
        """Test getting invoices by date with invalid format"""
        response = client.get(
            "/api/v1/invoices/by-date?date=invalid-date",
            headers=auth_headers_admin
        )
        
        assert response.status_code == 400
        assert "inválida" in response.json()["detail"].lower()
    
    def test_invoice_filter_by_month_year(self, client, auth_headers_admin, db, test_company, admin_user):
        """Test filtering invoices by month and year"""
        from app.models import Invoice
        from datetime import date
        
        # Create invoice for specific month/year
        today = date.today()
        invoice = Invoice(
            company_id=test_company.id,
            description="Monthly Invoice",
            amount=1000,
            due_date=today,
            created_by=admin_user.id
        )
        db.add(invoice)
        db.commit()
        
        response = client.get(
            f"/api/v1/invoices/?month={today.month}&year={today.year}",
            headers=auth_headers_admin
        )
        
        assert response.status_code == 200
        invoices = response.json()
        assert len(invoices) >= 1
    
    def test_invoice_filter_by_company_id(self, client, auth_headers_admin, db, test_company, admin_user):
        """Test filtering invoices by company ID"""
        from app.models import Invoice
        from datetime import date
        
        invoice = Invoice(
            company_id=test_company.id,
            description="Company Invoice",
            amount=1000,
            due_date=date.today(),
            created_by=admin_user.id
        )
        db.add(invoice)
        db.commit()
        
        response = client.get(
            f"/api/v1/invoices/?company_id={test_company.id}",
            headers=auth_headers_admin
        )
        
        assert response.status_code == 200
        invoices = response.json()
        for inv in invoices:
            assert inv["company_id"] == test_company.id
