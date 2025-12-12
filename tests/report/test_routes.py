import pytest
from datetime import date, timedelta
from app.order.models import Invoice


class TestReportRoutes:
    """Test report and analytics routes"""
    
    def test_get_stats_as_admin(self, client, admin_token, test_invoice):
        """Test getting dashboard stats as admin"""
        response = client.get(
            "/api/auth/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "paid" in data
        assert "pending" in data
        assert "overdue" in data
        assert "upcoming" in data
        assert "pending_amount" in data
    
    def test_get_stats_as_user(self, client, user_token, test_invoice):
        """Test getting dashboard stats as user"""
        response = client.get(
            "/api/auth/stats",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["total"], int)
        assert isinstance(data["pending_amount"], float)
    
    def test_get_stats_no_auth(self, client):
        """Test getting stats without authentication"""
        response = client.get("/api/auth/stats")
        
        assert response.status_code == 401
    
    def test_get_stats_with_invoices(self, client, admin_token, test_company, test_admin, db_session):
        """Test stats with known invoices"""
        # Create specific invoices for testing
        paid_invoice = Invoice(
            company_id=test_company.id,
            description="Paid",
            amount=1000.00,
            due_date=date.today(),
            is_paid=True,
            created_by=test_admin.id
        )
        pending_invoice = Invoice(
            company_id=test_company.id,
            description="Pending",
            amount=500.00,
            due_date=date.today() + timedelta(days=5),
            is_paid=False,
            created_by=test_admin.id
        )
        overdue_invoice = Invoice(
            company_id=test_company.id,
            description="Overdue",
            amount=750.00,
            due_date=date.today() - timedelta(days=5),
            is_paid=False,
            created_by=test_admin.id
        )
        db_session.add_all([paid_invoice, pending_invoice, overdue_invoice])
        db_session.commit()
        
        response = client.get(
            "/api/auth/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["paid"] >= 1
        assert data["pending"] >= 2  # pending + overdue
        assert data["overdue"] >= 1
        assert data["pending_amount"] >= 1250.00  # 500 + 750


class TestCalendarRoutes:
    """Test calendar routes"""
    
    def test_get_calendar_current_month(self, client, admin_token, test_invoice):
        """Test getting calendar for current month"""
        today = date.today()
        response = client.get(
            f"/api/invoices/calendar?month={today.month}&year={today.year}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.json()}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["month"] == today.month
        assert data["year"] == today.year
        assert "days" in data
    
    def test_get_calendar_specific_month(self, client, admin_token):
        """Test getting calendar for specific month"""
        response = client.get(
            "/api/invoices/calendar?month=6&year=2024",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["month"] == 6
        assert data["year"] == 2024
    
    def test_get_calendar_as_user(self, client, user_token, test_invoice):
        """Test getting calendar as user (filtered by company)"""
        today = date.today()
        response = client.get(
            f"/api/invoices/calendar?month={today.month}&year={today.year}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "days" in data
    
    def test_get_calendar_with_company_filter(self, client, admin_token, test_company, test_invoice):
        """Test getting calendar with company filter"""
        today = date.today()
        response = client.get(
            f"/api/invoices/calendar?month={today.month}&year={today.year}&company_id={test_company.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["days"], dict)
    
    def test_get_calendar_no_auth(self, client):
        """Test getting calendar without authentication"""
        response = client.get("/api/invoices/calendar?month=1&year=2024")
        
        assert response.status_code == 401
    
    def test_get_calendar_with_data(self, client, admin_token, test_company, test_admin, db_session):
        """Test calendar with known invoice data"""
        today = date.today()
        
        # Create invoice on today
        invoice = Invoice(
            company_id=test_company.id,
            description="Today's Invoice",
            amount=1500.00,
            due_date=today,
            is_paid=False,
            created_by=test_admin.id
        )
        db_session.add(invoice)
        db_session.commit()
        
        response = client.get(
            f"/api/invoices/calendar?month={today.month}&year={today.year}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check if today has invoice data
        if today.day in [int(k) for k in data["days"].keys()]:
            day_data = data["days"][str(today.day)]
            assert day_data["total"] >= 1
            assert day_data["amount"] >= 1500.00


class TestIntegrationReports:
    """Integration tests for reports combining multiple features"""
    
    def test_complete_reporting_workflow(self, client, admin_token, test_company, test_admin, db_session):
        """Test complete reporting workflow: create invoices, get stats, get calendar"""
        today = date.today()
        
        # Step 1: Create various invoices
        invoices = [
            Invoice(
                company_id=test_company.id,
                description="Paid Invoice",
                amount=1000.00,
                due_date=today - timedelta(days=10),
                is_paid=True,
                created_by=test_admin.id
            ),
            Invoice(
                company_id=test_company.id,
                description="Upcoming Invoice",
                amount=2000.00,
                due_date=today + timedelta(days=3),
                is_paid=False,
                created_by=test_admin.id
            ),
            Invoice(
                company_id=test_company.id,
                description="Overdue Invoice",
                amount=1500.00,
                due_date=today - timedelta(days=5),
                is_paid=False,
                created_by=test_admin.id
            ),
        ]
        db_session.add_all(invoices)
        db_session.commit()
        
        # Step 2: Get stats
        stats_response = client.get(
            "/api/auth/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert stats["total"] >= 3
        assert stats["paid"] >= 1
        assert stats["overdue"] >= 1
        assert stats["upcoming"] >= 1
        
        # Step 3: Get calendar
        calendar_response = client.get(
            f"/api/invoices/calendar?month={today.month}&year={today.year}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert calendar_response.status_code == 200
        calendar = calendar_response.json()
        assert "days" in calendar
        
        # Step 4: Verify data consistency
        # Total invoices in stats should match or exceed what we created
        assert stats["pending_amount"] >= 3500.00  # 2000 + 1500
    
    def test_user_vs_admin_reporting_access(self, client, user_token, admin_token, test_company, test_admin, db_session):
        """Test that users see filtered data while admins see all data"""
        # Create invoices for the test company
        invoice1 = Invoice(
            company_id=test_company.id,
            description="Company Invoice",
            amount=1000.00,
            due_date=date.today(),
            is_paid=False,
            created_by=test_admin.id
        )
        db_session.add(invoice1)
        
        # Create another company with invoice
        from app.order.models import Company
        other_company = Company(name="Other Co", cnpj="88.888.888/0001-88")
        db_session.add(other_company)
        db_session.commit()
        
        invoice2 = Invoice(
            company_id=other_company.id,
            description="Other Company Invoice",
            amount=2000.00,
            due_date=date.today(),
            is_paid=False,
            created_by=test_admin.id
        )
        db_session.add(invoice2)
        db_session.commit()
        
        # Get stats as user (should only see own company)
        user_stats = client.get(
            "/api/auth/stats",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert user_stats.status_code == 200
        user_data = user_stats.json()
        
        # Get stats as admin (should see all)
        admin_stats = client.get(
            "/api/auth/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert admin_stats.status_code == 200
        admin_data = admin_stats.json()
        
        # Admin should see more or equal invoices than user
        assert admin_data["total"] >= user_data["total"]
        assert admin_data["pending_amount"] >= user_data["pending_amount"]
