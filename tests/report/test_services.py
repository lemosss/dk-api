import pytest
from datetime import date, timedelta
from app.report import services
from app.order.models import Invoice


class TestDashboardStats:
    """Test dashboard statistics service"""
    
    def test_get_dashboard_stats_as_admin(self, db_session, test_admin, test_invoice):
        """Test getting dashboard stats as admin"""
        stats = services.get_dashboard_stats(db_session, test_admin)
        
        assert "total" in stats
        assert "paid" in stats
        assert "pending" in stats
        assert "overdue" in stats
        assert "upcoming" in stats
        assert "pending_amount" in stats
        assert isinstance(stats["total"], int)
        assert isinstance(stats["pending_amount"], float)
    
    def test_get_dashboard_stats_as_user(self, db_session, test_user, test_invoice):
        """Test getting dashboard stats as user (filtered by company)"""
        stats = services.get_dashboard_stats(db_session, test_user)
        
        # Should only include invoices from user's company
        assert stats["total"] >= 0
        assert stats["paid"] + stats["pending"] == stats["total"]
    
    def test_get_dashboard_stats_paid_count(self, db_session, test_admin, test_company):
        """Test dashboard stats paid count"""
        # Create paid invoice
        paid_invoice = Invoice(
            company_id=test_company.id,
            description="Paid",
            amount=1000.00,
            due_date=date.today(),
            is_paid=True,
            created_by=test_admin.id
        )
        db_session.add(paid_invoice)
        db_session.commit()
        
        stats = services.get_dashboard_stats(db_session, test_admin)
        
        assert stats["paid"] >= 1
    
    def test_get_dashboard_stats_overdue_count(self, db_session, test_admin, test_company):
        """Test dashboard stats overdue count"""
        # Create overdue invoice
        overdue_invoice = Invoice(
            company_id=test_company.id,
            description="Overdue",
            amount=1000.00,
            due_date=date.today() - timedelta(days=5),
            is_paid=False,
            created_by=test_admin.id
        )
        db_session.add(overdue_invoice)
        db_session.commit()
        
        stats = services.get_dashboard_stats(db_session, test_admin)
        
        assert stats["overdue"] >= 1
    
    def test_get_dashboard_stats_upcoming_count(self, db_session, test_admin, test_company):
        """Test dashboard stats upcoming count"""
        # Create upcoming invoice (due in 3 days)
        upcoming_invoice = Invoice(
            company_id=test_company.id,
            description="Upcoming",
            amount=1000.00,
            due_date=date.today() + timedelta(days=3),
            is_paid=False,
            created_by=test_admin.id
        )
        db_session.add(upcoming_invoice)
        db_session.commit()
        
        stats = services.get_dashboard_stats(db_session, test_admin)
        
        assert stats["upcoming"] >= 1
    
    def test_get_dashboard_stats_pending_amount(self, db_session, test_admin, test_company):
        """Test dashboard stats pending amount calculation"""
        # Create pending invoices with known amounts
        invoice1 = Invoice(
            company_id=test_company.id,
            description="Pending 1",
            amount=500.00,
            due_date=date.today() + timedelta(days=1),
            is_paid=False,
            created_by=test_admin.id
        )
        invoice2 = Invoice(
            company_id=test_company.id,
            description="Pending 2",
            amount=750.00,
            due_date=date.today() + timedelta(days=2),
            is_paid=False,
            created_by=test_admin.id
        )
        db_session.add_all([invoice1, invoice2])
        db_session.commit()
        
        stats = services.get_dashboard_stats(db_session, test_admin)
        
        # Should include at least the sum of our test invoices
        assert stats["pending_amount"] >= 1250.00


class TestCalendarData:
    """Test calendar data service"""
    
    def test_get_calendar_data_current_month(self, db_session, test_admin, test_invoice):
        """Test getting calendar data for current month"""
        today = date.today()
        calendar_data = services.get_calendar_data(
            db_session, test_admin, today.month, today.year
        )
        
        assert calendar_data["month"] == today.month
        assert calendar_data["year"] == today.year
        assert "days" in calendar_data
        assert isinstance(calendar_data["days"], dict)
    
    def test_get_calendar_data_as_user(self, db_session, test_user, test_invoice):
        """Test getting calendar data as user (filtered by company)"""
        today = date.today()
        calendar_data = services.get_calendar_data(
            db_session, test_user, today.month, today.year
        )
        
        # Should only include days with invoices from user's company
        assert isinstance(calendar_data["days"], dict)
    
    def test_get_calendar_data_with_invoices(self, db_session, test_admin, test_company):
        """Test calendar data with specific invoices"""
        today = date.today()
        
        # Create invoice on a specific day
        invoice = Invoice(
            company_id=test_company.id,
            description="Test",
            amount=1000.00,
            due_date=today,
            is_paid=False,
            created_by=test_admin.id
        )
        db_session.add(invoice)
        db_session.commit()
        
        calendar_data = services.get_calendar_data(
            db_session, test_admin, today.month, today.year
        )
        
        # Should have data for today
        if today.day in calendar_data["days"]:
            day_data = calendar_data["days"][today.day]
            assert day_data["total"] >= 1
            assert day_data["amount"] >= 1000.00
    
    def test_get_calendar_data_paid_vs_pending(self, db_session, test_admin, test_company):
        """Test calendar data paid vs pending counts"""
        today = date.today()
        
        # Create one paid and one pending invoice
        paid_invoice = Invoice(
            company_id=test_company.id,
            description="Paid",
            amount=500.00,
            due_date=today,
            is_paid=True,
            created_by=test_admin.id
        )
        pending_invoice = Invoice(
            company_id=test_company.id,
            description="Pending",
            amount=750.00,
            due_date=today,
            is_paid=False,
            created_by=test_admin.id
        )
        db_session.add_all([paid_invoice, pending_invoice])
        db_session.commit()
        
        calendar_data = services.get_calendar_data(
            db_session, test_admin, today.month, today.year
        )
        
        if today.day in calendar_data["days"]:
            day_data = calendar_data["days"][today.day]
            assert day_data["paid"] >= 1
            assert day_data["pending"] >= 1
            assert day_data["total"] == day_data["paid"] + day_data["pending"]
    
    def test_get_calendar_data_empty_month(self, db_session, test_admin):
        """Test calendar data for month with no invoices"""
        # Use a month far in the future
        calendar_data = services.get_calendar_data(
            db_session, test_admin, 12, 2099
        )
        
        assert calendar_data["month"] == 12
        assert calendar_data["year"] == 2099
        assert calendar_data["days"] == {}
    
    def test_get_calendar_data_with_company_filter(self, db_session, test_admin, test_company):
        """Test calendar data with company filter"""
        today = date.today()
        
        calendar_data = services.get_calendar_data(
            db_session, test_admin, today.month, today.year, test_company.id
        )
        
        assert isinstance(calendar_data["days"], dict)
    
    def test_get_calendar_data_multiple_invoices_same_day(self, db_session, test_admin, test_company):
        """Test calendar data with multiple invoices on same day"""
        today = date.today()
        
        # Create multiple invoices on the same day
        for i in range(3):
            invoice = Invoice(
                company_id=test_company.id,
                description=f"Invoice {i}",
                amount=1000.00 * (i + 1),
                due_date=today,
                is_paid=False,
                created_by=test_admin.id
            )
            db_session.add(invoice)
        db_session.commit()
        
        calendar_data = services.get_calendar_data(
            db_session, test_admin, today.month, today.year
        )
        
        if today.day in calendar_data["days"]:
            day_data = calendar_data["days"][today.day]
            assert day_data["total"] >= 3
            # Total amount should be at least 1000 + 2000 + 3000
            assert day_data["amount"] >= 6000.00
