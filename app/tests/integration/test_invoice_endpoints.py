import pytest
from datetime import date, timedelta
from io import BytesIO


class TestInvoiceEndpoints:
    """Test invoice management endpoints"""
    
    def test_list_invoices_as_admin(self, client, auth_headers_admin, db, test_company, admin_user):
        """Test listing invoices as admin"""
        from app.models import Invoice
        
        # Create test invoice
        invoice = Invoice(
            company_id=test_company.id,
            description="Test Invoice",
            amount=1000,
            due_date=date.today(),
            created_by=admin_user.id
        )
        db.add(invoice)
        db.commit()
        
        response = client.get("/api/v1/invoices/", headers=auth_headers_admin)
        
        assert response.status_code == 200
        invoices = response.json()
        assert isinstance(invoices, list)
        assert len(invoices) >= 1
    
    def test_list_invoices_as_user(self, client, auth_headers_user, db, test_company, regular_user):
        """Test listing invoices as user (should see only their company's invoices)"""
        from app.models import Invoice
        
        # Create invoice for user's company
        invoice = Invoice(
            company_id=test_company.id,
            description="User Invoice",
            amount=500,
            due_date=date.today(),
            created_by=regular_user.id
        )
        db.add(invoice)
        db.commit()
        
        response = client.get("/api/v1/invoices/", headers=auth_headers_user)
        
        assert response.status_code == 200
        invoices = response.json()
        # All invoices should be from user's company
        for inv in invoices:
            assert inv["company_id"] == regular_user.company_id
    
    def test_list_invoices_with_filters(self, client, auth_headers_admin, db, test_company, admin_user):
        """Test listing invoices with filters"""
        from app.models import Invoice
        
        # Create paid and unpaid invoices
        paid = Invoice(
            company_id=test_company.id,
            description="Paid",
            amount=1000,
            due_date=date.today(),
            is_paid=True,
            created_by=admin_user.id
        )
        unpaid = Invoice(
            company_id=test_company.id,
            description="Unpaid",
            amount=2000,
            due_date=date.today(),
            is_paid=False,
            created_by=admin_user.id
        )
        db.add_all([paid, unpaid])
        db.commit()
        
        # Filter by is_paid=True
        response = client.get(
            "/api/v1/invoices/?is_paid=true",
            headers=auth_headers_admin
        )
        
        assert response.status_code == 200
        invoices = response.json()
        for inv in invoices:
            assert inv["is_paid"] is True
    
    def test_get_invoice_by_id(self, client, auth_headers_admin, db, test_company, admin_user):
        """Test getting invoice by ID"""
        from app.models import Invoice
        
        invoice = Invoice(
            company_id=test_company.id,
            description="Test",
            amount=1000,
            due_date=date.today(),
            created_by=admin_user.id
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        response = client.get(
            f"/api/v1/invoices/{invoice.id}",
            headers=auth_headers_admin
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == invoice.id
        assert data["description"] == "Test"
    
    def test_get_invoice_as_user_own_company(self, client, auth_headers_user, db, test_company, regular_user):
        """Test user getting invoice from their company"""
        from app.models import Invoice
        
        invoice = Invoice(
            company_id=test_company.id,
            description="Test",
            amount=1000,
            due_date=date.today(),
            created_by=regular_user.id
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        response = client.get(
            f"/api/v1/invoices/{invoice.id}",
            headers=auth_headers_user
        )
        
        assert response.status_code == 200
    
    def test_get_invoice_as_user_other_company(self, client, auth_headers_user, db, admin_user):
        """Test user getting invoice from another company (should be forbidden)"""
        from app.models import Company, Invoice
        
        # Create another company and invoice
        other_company = Company(name="Other", cnpj="98.765.432/0001-10")
        db.add(other_company)
        db.commit()
        db.refresh(other_company)
        
        invoice = Invoice(
            company_id=other_company.id,
            description="Other",
            amount=1000,
            due_date=date.today(),
            created_by=admin_user.id
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        response = client.get(
            f"/api/v1/invoices/{invoice.id}",
            headers=auth_headers_user
        )
        
        assert response.status_code == 403
    
    def test_create_invoice(self, client, auth_headers_admin, test_company):
        """Test creating a new invoice"""
        invoice_data = {
            "company_id": test_company.id,
            "description": "New Invoice",
            "amount": 1500.00,
            "due_date": str(date.today() + timedelta(days=30)),
            "notes": "Test notes"
        }
        
        response = client.post(
            "/api/v1/invoices/",
            json=invoice_data,
            headers=auth_headers_admin
        )
        
        assert response.status_code == 201
        invoice = response.json()
        assert invoice["description"] == "New Invoice"
        assert invoice["amount"] == 1500.00
    
    def test_create_invoice_as_user_forbidden(self, client, auth_headers_user, test_company):
        """Test creating invoice as user (should be forbidden)"""
        invoice_data = {
            "company_id": test_company.id,
            "description": "Test",
            "amount": 1000,
            "due_date": str(date.today())
        }
        
        response = client.post(
            "/api/v1/invoices/",
            json=invoice_data,
            headers=auth_headers_user
        )
        
        assert response.status_code == 403
    
    def test_update_invoice(self, client, auth_headers_admin, db, test_company, admin_user):
        """Test updating an invoice"""
        from app.models import Invoice
        
        invoice = Invoice(
            company_id=test_company.id,
            description="Original",
            amount=1000,
            due_date=date.today(),
            created_by=admin_user.id
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        update_data = {"description": "Updated"}
        
        response = client.put(
            f"/api/v1/invoices/{invoice.id}",
            json=update_data,
            headers=auth_headers_admin
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated"
    
    def test_toggle_paid_status(self, client, auth_headers_admin, db, test_company, admin_user):
        """Test toggling paid status"""
        from app.models import Invoice
        
        invoice = Invoice(
            company_id=test_company.id,
            description="Test",
            amount=1000,
            due_date=date.today(),
            is_paid=False,
            created_by=admin_user.id
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        response = client.patch(
            f"/api/v1/invoices/{invoice.id}/toggle-paid",
            headers=auth_headers_admin
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_paid"] is True
        assert data["paid_at"] is not None
    
    def test_toggle_paid_as_user_own_company(self, client, auth_headers_user, db, test_company, regular_user):
        """Test user toggling paid status for their company's invoice"""
        from app.models import Invoice
        
        invoice = Invoice(
            company_id=test_company.id,
            description="Test",
            amount=1000,
            due_date=date.today(),
            is_paid=False,
            created_by=regular_user.id
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        response = client.patch(
            f"/api/v1/invoices/{invoice.id}/toggle-paid",
            headers=auth_headers_user
        )
        
        assert response.status_code == 200
    
    def test_delete_invoice(self, client, auth_headers_admin, db, test_company, admin_user):
        """Test deleting an invoice"""
        from app.models import Invoice
        
        invoice = Invoice(
            company_id=test_company.id,
            description="To Delete",
            amount=1000,
            due_date=date.today(),
            created_by=admin_user.id
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        response = client.delete(
            f"/api/v1/invoices/{invoice.id}",
            headers=auth_headers_admin
        )
        
        assert response.status_code == 204
    
    def test_delete_invoice_as_user_forbidden(self, client, auth_headers_user, db, test_company, regular_user):
        """Test deleting invoice as user (should be forbidden)"""
        from app.models import Invoice
        
        invoice = Invoice(
            company_id=test_company.id,
            description="Test",
            amount=1000,
            due_date=date.today(),
            created_by=regular_user.id
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        response = client.delete(
            f"/api/v1/invoices/{invoice.id}",
            headers=auth_headers_user
        )
        
        assert response.status_code == 403
    
    def test_get_calendar_data(self, client, auth_headers_admin, db, test_company, admin_user):
        """Test getting calendar data"""
        from app.models import Invoice
        
        today = date.today()
        invoice = Invoice(
            company_id=test_company.id,
            description="Test",
            amount=1000,
            due_date=today,
            created_by=admin_user.id
        )
        db.add(invoice)
        db.commit()
        
        response = client.get(
            f"/api/v1/invoices/calendar?month={today.month}&year={today.year}",
            headers=auth_headers_admin
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "days" in data
        assert "month" in data
        assert "year" in data
    
    def test_get_invoices_by_date(self, client, auth_headers_admin, db, test_company, admin_user):
        """Test getting invoices by specific date"""
        from app.models import Invoice
        
        today = date.today()
        invoice = Invoice(
            company_id=test_company.id,
            description="Test",
            amount=1000,
            due_date=today,
            created_by=admin_user.id
        )
        db.add(invoice)
        db.commit()
        
        response = client.get(
            f"/api/v1/invoices/by-date?date={today.isoformat()}",
            headers=auth_headers_admin
        )
        
        assert response.status_code == 200
        invoices = response.json()
        assert isinstance(invoices, list)

    def test_upload_invoice_file(self, client, auth_headers_admin, db, test_company, admin_user):
        """Test uploading PDF file to invoice"""
        from app.models import Invoice
        
        # Create invoice
        invoice = Invoice(
            company_id=test_company.id,
            description="Test",
            amount=1000,
            due_date=date.today(),
            created_by=admin_user.id
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        # Create a fake PDF file
        pdf_content = b"%PDF-1.4 test content"
        files = {"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")}
        
        response = client.post(
            f"/api/v1/invoices/{invoice.id}/upload",
            files=files,
            headers=auth_headers_admin
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "file_url" in data
        assert data["file_url"].startswith("/uploads/")
    
    def test_upload_invoice_file_invalid_type(self, client, auth_headers_admin, db, test_company, admin_user):
        """Test uploading non-PDF file"""
        from app.models import Invoice
        
        invoice = Invoice(
            company_id=test_company.id,
            description="Test",
            amount=1000,
            due_date=date.today(),
            created_by=admin_user.id
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        # Try to upload a non-PDF file
        files = {"file": ("test.jpg", BytesIO(b"fake image"), "image/jpeg")}
        
        response = client.post(
            f"/api/v1/invoices/{invoice.id}/upload",
            files=files,
            headers=auth_headers_admin
        )
        
        assert response.status_code == 400
    
    def test_upload_invoice_file_as_user_forbidden(self, client, auth_headers_user, db, test_company, regular_user):
        """Test uploading file as user (should be forbidden)"""
        from app.models import Invoice
        
        invoice = Invoice(
            company_id=test_company.id,
            description="Test",
            amount=1000,
            due_date=date.today(),
            created_by=regular_user.id
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        files = {"file": ("test.pdf", BytesIO(b"%PDF-1.4"), "application/pdf")}
        
        response = client.post(
            f"/api/v1/invoices/{invoice.id}/upload",
            files=files,
            headers=auth_headers_user
        )
        
        assert response.status_code == 403
