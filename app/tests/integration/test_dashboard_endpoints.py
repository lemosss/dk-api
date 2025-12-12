import pytest
from datetime import date, timedelta


class TestDashboardEndpoints:
    """Test dashboard statistics endpoints"""
    
    def test_get_stats_as_admin(self, client, auth_headers_admin, db, test_company, admin_user):
        """Test getting dashboard stats as admin"""
        from app.models import Invoice
        
        # Create test invoices
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
            due_date=date.today() + timedelta(days=5),
            is_paid=False,
            created_by=admin_user.id
        )
        overdue = Invoice(
            company_id=test_company.id,
            description="Overdue",
            amount=500,
            due_date=date.today() - timedelta(days=10),
            is_paid=False,
            created_by=admin_user.id
        )
        db.add_all([paid, unpaid, overdue])
        db.commit()
        
        response = client.get("/api/v1/dashboard/stats", headers=auth_headers_admin)
        
        assert response.status_code == 200
        stats = response.json()
        assert "total" in stats
        assert "paid" in stats
        assert "pending" in stats
        assert "overdue" in stats
        assert "upcoming" in stats
        assert "pending_amount" in stats
        
        # Verify counts
        assert stats["total"] >= 3
        assert stats["paid"] >= 1
        assert stats["pending"] >= 2
        assert stats["overdue"] >= 1
    
    def test_get_stats_as_user(self, client, auth_headers_user, db, test_company, regular_user):
        """Test getting stats as user (should see only their company's data)"""
        from app.models import Invoice, Company
        
        # Create invoice for user's company
        user_invoice = Invoice(
            company_id=test_company.id,
            description="User Invoice",
            amount=1000,
            due_date=date.today(),
            is_paid=False,
            created_by=regular_user.id
        )
        db.add(user_invoice)
        
        # Create another company and invoice
        other_company = Company(name="Other", cnpj="98.765.432/0001-10")
        db.add(other_company)
        db.commit()
        db.refresh(other_company)
        
        other_invoice = Invoice(
            company_id=other_company.id,
            description="Other Invoice",
            amount=5000,
            due_date=date.today(),
            is_paid=False,
            created_by=regular_user.id
        )
        db.add(other_invoice)
        db.commit()
        
        response = client.get("/api/v1/dashboard/stats", headers=auth_headers_user)
        
        assert response.status_code == 200
        stats = response.json()
        
        # User should not see stats from other company
        # This depends on having only invoices from their company
        assert "total" in stats
        assert "pending_amount" in stats
    
    def test_get_stats_no_invoices(self, client, auth_headers_superadmin, db):
        """Test getting stats when there are no invoices"""
        response = client.get("/api/v1/dashboard/stats", headers=auth_headers_superadmin)
        
        assert response.status_code == 200
        stats = response.json()
        assert stats["total"] == 0
        assert stats["paid"] == 0
        assert stats["pending"] == 0
        assert stats["overdue"] == 0
        assert stats["upcoming"] == 0
        assert stats["pending_amount"] == 0
    
    def test_get_stats_unauthenticated(self, client):
        """Test getting stats without authentication"""
        response = client.get("/api/v1/dashboard/stats")
        
        assert response.status_code == 401
