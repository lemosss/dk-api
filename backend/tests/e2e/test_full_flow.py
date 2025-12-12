import pytest
from datetime import date, timedelta


class TestFullFlow:
    """End-to-end test for complete workflow"""
    
    def test_complete_invoice_management_flow(self, client, db):
        """Test complete flow from user creation to invoice management"""
        
        # Step 1: Create a company
        company_data = {
            "name": "E2E Test Company",
            "cnpj": "11.222.333/0001-99",
            "email": "e2e@company.com"
        }
        
        # We need a superadmin to create company
        from app.models import User, RoleEnum
        from app.core.security import get_password_hash
        
        superadmin = User(
            email="e2e_super@test.com",
            hashed_password=get_password_hash("super123"),
            role=RoleEnum.superadmin,
            is_active=True
        )
        db.add(superadmin)
        db.commit()
        
        # Login as superadmin
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "e2e_super@test.com", "password": "super123"}
        )
        assert login_response.status_code == 200
        super_token = login_response.json()["access_token"]
        super_headers = {"Authorization": f"Bearer {super_token}"}
        
        # Create admin user
        admin_data = {
            "email": "e2e_admin@test.com",
            "password": "admin123",
            "name": "E2E Admin",
            "role": "admin"
        }
        admin_response = client.post(
            "/api/v1/users/",
            json=admin_data,
            headers=super_headers
        )
        assert admin_response.status_code == 201
        
        # Login as admin
        admin_login = client.post(
            "/api/v1/auth/login",
            data={"username": "e2e_admin@test.com", "password": "admin123"}
        )
        assert admin_login.status_code == 200
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Step 2: Create company as admin
        company_response = client.post(
            "/api/v1/companies/",
            json=company_data,
            headers=admin_headers
        )
        assert company_response.status_code == 201
        company = company_response.json()
        company_id = company["id"]
        
        # Step 3: Create a regular user for this company
        user_data = {
            "email": "e2e_user@test.com",
            "password": "user123",
            "name": "E2E User",
            "role": "user",
            "company_id": company_id
        }
        user_response = client.post(
            "/api/v1/users/",
            json=user_data,
            headers=super_headers
        )
        assert user_response.status_code == 201
        
        # Login as regular user
        user_login = client.post(
            "/api/v1/auth/login",
            data={"username": "e2e_user@test.com", "password": "user123"}
        )
        assert user_login.status_code == 200
        user_token = user_login.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        # Step 4: Admin creates an invoice
        invoice_data = {
            "company_id": company_id,
            "description": "E2E Test Invoice",
            "amount": 2500.00,
            "due_date": str(date.today() + timedelta(days=15)),
            "notes": "Test invoice for E2E flow"
        }
        invoice_response = client.post(
            "/api/v1/invoices/",
            json=invoice_data,
            headers=admin_headers
        )
        assert invoice_response.status_code == 201
        invoice = invoice_response.json()
        invoice_id = invoice["id"]
        assert invoice["description"] == "E2E Test Invoice"
        assert invoice["amount"] == 2500.00
        assert invoice["is_paid"] is False
        
        # Step 5: User views their invoices
        user_invoices = client.get("/api/v1/invoices/", headers=user_headers)
        assert user_invoices.status_code == 200
        invoices = user_invoices.json()
        assert len(invoices) >= 1
        assert any(inv["id"] == invoice_id for inv in invoices)
        
        # Step 6: User gets specific invoice
        get_invoice = client.get(f"/api/v1/invoices/{invoice_id}", headers=user_headers)
        assert get_invoice.status_code == 200
        
        # Step 7: User toggles paid status
        toggle_response = client.patch(
            f"/api/v1/invoices/{invoice_id}/toggle-paid",
            headers=user_headers
        )
        assert toggle_response.status_code == 200
        toggled_invoice = toggle_response.json()
        assert toggled_invoice["is_paid"] is True
        assert toggled_invoice["paid_at"] is not None
        
        # Step 8: User views dashboard stats
        stats_response = client.get("/api/v1/dashboard/stats", headers=user_headers)
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert stats["total"] >= 1
        assert stats["paid"] >= 1
        
        # Step 9: Admin updates the invoice
        update_data = {"notes": "Updated notes by admin"}
        update_response = client.put(
            f"/api/v1/invoices/{invoice_id}",
            json=update_data,
            headers=admin_headers
        )
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["notes"] == "Updated notes by admin"
        
        # Step 10: User cannot delete invoice (forbidden)
        delete_attempt = client.delete(
            f"/api/v1/invoices/{invoice_id}",
            headers=user_headers
        )
        assert delete_attempt.status_code == 403
        
        # Step 11: Admin can delete invoice
        delete_response = client.delete(
            f"/api/v1/invoices/{invoice_id}",
            headers=admin_headers
        )
        assert delete_response.status_code == 204
        
        # Step 12: Verify invoice is deleted
        get_deleted = client.get(
            f"/api/v1/invoices/{invoice_id}",
            headers=admin_headers
        )
        assert get_deleted.status_code == 404
    
    def test_authentication_flow(self, client, db):
        """Test authentication and authorization flow"""
        from app.models import User, RoleEnum
        from app.core.security import get_password_hash
        
        # Create test user
        user = User(
            email="auth_test@test.com",
            hashed_password=get_password_hash("password123"),
            role=RoleEnum.user,
            is_active=True
        )
        db.add(user)
        db.commit()
        
        # Step 1: Login
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "auth_test@test.com", "password": "password123"}
        )
        assert login_response.status_code == 200
        token_data = login_response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 2: Get current user info
        me_response = client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        user_info = me_response.json()
        assert user_info["email"] == "auth_test@test.com"
        assert user_info["role"] == "user"
        
        # Step 3: Try to access protected endpoint without token
        no_auth_response = client.get("/api/v1/auth/me")
        assert no_auth_response.status_code == 401
        
        # Step 4: Try to access admin endpoint as regular user (forbidden)
        forbidden_response = client.get("/api/v1/users/", headers=headers)
        assert forbidden_response.status_code == 403
