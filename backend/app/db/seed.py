from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.db.database import SessionLocal, engine
from app.models import Base, User, Company, Invoice, RoleEnum
from app.core.security import get_password_hash


def seed_database():
    """Populate database with initial data for development"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        # Check if database already has data
        if db.query(User).count() > 0:
            print("Database already seeded. Skipping...")
            return
        
        print("Seeding database...")
        
        # Create companies
        company1 = Company(
            name="ACME Corporation",
            cnpj="12.345.678/0001-90",
            email="contato@acme.com",
            phone="(11) 1234-5678",
            address="Av. Paulista, 1000 - São Paulo, SP"
        )
        company2 = Company(
            name="TechStart Ltda",
            cnpj="98.765.432/0001-10",
            email="contato@techstart.com",
            phone="(21) 9876-5432",
            address="Rua das Flores, 200 - Rio de Janeiro, RJ"
        )
        db.add_all([company1, company2])
        db.commit()
        db.refresh(company1)
        db.refresh(company2)
        
        # Create users
        superadmin = User(
            email="super@example.com",
            hashed_password=get_password_hash("super123"),
            name="Super Admin",
            role=RoleEnum.superadmin,
            is_active=True
        )
        admin = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            name="Admin User",
            role=RoleEnum.admin,
            is_active=True
        )
        user1 = User(
            email="user@acme.com",
            hashed_password=get_password_hash("user123"),
            name="ACME User",
            role=RoleEnum.user,
            company_id=company1.id,
            is_active=True
        )
        user2 = User(
            email="user@techstart.com",
            hashed_password=get_password_hash("user123"),
            name="TechStart User",
            role=RoleEnum.user,
            company_id=company2.id,
            is_active=True
        )
        db.add_all([superadmin, admin, user1, user2])
        db.commit()
        db.refresh(superadmin)
        
        # Create invoices
        today = date.today()
        invoices = [
            # ACME invoices
            Invoice(
                company_id=company1.id,
                description="Licença de Software - Janeiro",
                amount=5000.00,
                due_date=today + timedelta(days=5),
                is_paid=False,
                created_by=superadmin.id
            ),
            Invoice(
                company_id=company1.id,
                description="Manutenção Servidor",
                amount=2500.00,
                due_date=today + timedelta(days=15),
                is_paid=True,
                created_by=superadmin.id
            ),
            Invoice(
                company_id=company1.id,
                description="Consultoria TI",
                amount=8000.00,
                due_date=today - timedelta(days=10),
                is_paid=False,
                created_by=superadmin.id,
                notes="Pagamento atrasado"
            ),
            # TechStart invoices
            Invoice(
                company_id=company2.id,
                description="Hospedagem Cloud - Q1",
                amount=3500.00,
                due_date=today + timedelta(days=20),
                is_paid=False,
                created_by=superadmin.id
            ),
            Invoice(
                company_id=company2.id,
                description="Suporte Técnico",
                amount=1500.00,
                due_date=today + timedelta(days=7),
                is_paid=True,
                created_by=superadmin.id
            ),
            Invoice(
                company_id=company2.id,
                description="Desenvolvimento App Mobile",
                amount=15000.00,
                due_date=today + timedelta(days=30),
                is_paid=False,
                created_by=superadmin.id
            ),
        ]
        db.add_all(invoices)
        db.commit()
        
        print("Database seeded successfully!")
        print("\nTest users:")
        print("  Super Admin: super@example.com / super123")
        print("  Admin: admin@example.com / admin123")
        print("  ACME User: user@acme.com / user123")
        print("  TechStart User: user@techstart.com / user123")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
