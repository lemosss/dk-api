"""
Seed script to populate the database with initial data
"""
from app.common.database import SessionLocal, engine, Base
from app.user.models import User, RoleEnum
from app.order.models import Company, Invoice
from app.user.auth import hash_password
from app.common.config import settings
from datetime import date, timedelta
import random


def run_seed():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(User).first():
            print("⚠️  Database already has data. Skipping seed.")
            return
        
        print("🌱 Seeding database...")
        
        # Create companies
        companies = [
            Company(
                name="ACME Corporation",
                cnpj="00.000.000/0001-00",
                email="contato@acme.com.br",
                phone="(11) 3000-0001",
                address="Av. Paulista, 1000, São Paulo - SP"
            ),
            Company(
                name="TechStart Ltda",
                cnpj="11.111.111/0001-11",
                email="financeiro@techstart.com.br",
                phone="(11) 3000-0002",
                address="Rua Augusta, 500, São Paulo - SP"
            ),
            Company(
                name="Beta Solutions",
                cnpj="22.222.222/0001-22",
                email="contato@betasolutions.com",
                phone="(21) 3000-0003",
                address="Av. Rio Branco, 100, Rio de Janeiro - RJ"
            )
        ]
        
        for company in companies:
            db.add(company)
        db.commit()
        
        for company in companies:
            db.refresh(company)
        
        print(f"✅ Created {len(companies)} companies")
        
        # Create users
        users = [
            User(
                email=settings.SUPERADMIN_EMAIL,
                hashed_password=hash_password(settings.SUPERADMIN_PASSWORD),
                name="Super Admin",
                role=RoleEnum.superadmin
            ),
            User(
                email="admin@example.com",
                hashed_password=hash_password("admin123"),
                name="Administrador",
                role=RoleEnum.admin
            ),
            User(
                email="user@acme.com",
                hashed_password=hash_password("user123"),
                name="João Silva",
                role=RoleEnum.user,
                company_id=companies[0].id
            ),
            User(
                email="user@techstart.com",
                hashed_password=hash_password("user123"),
                name="Maria Santos",
                role=RoleEnum.user,
                company_id=companies[1].id
            )
        ]
        
        for user in users:
            db.add(user)
        db.commit()
        
        for user in users:
            db.refresh(user)
        
        print(f"✅ Created {len(users)} users")
        
        # Create invoices
        admin_user = users[1]  # Admin creates the invoices
        today = date.today()
        
        invoice_descriptions = [
            "Serviços de consultoria",
            "Manutenção mensal",
            "Licença de software",
            "Hospedagem cloud",
            "Suporte técnico",
            "Desenvolvimento web",
            "Marketing digital",
            "Design gráfico",
            "Treinamento",
            "Equipamentos de TI"
        ]
        
        invoices = []
        
        # Create invoices for each company
        for company in companies:
            # Some past invoices (paid)
            for i in range(3):
                inv = Invoice(
                    company_id=company.id,
                    description=random.choice(invoice_descriptions),
                    amount=round(random.uniform(500, 5000), 2),
                    due_date=today - timedelta(days=random.randint(10, 60)),
                    is_paid=True,
                    created_by=admin_user.id,
                    notes="Pagamento realizado via boleto"
                )
                invoices.append(inv)
            
            # Some overdue invoices (not paid)
            for i in range(2):
                inv = Invoice(
                    company_id=company.id,
                    description=random.choice(invoice_descriptions),
                    amount=round(random.uniform(500, 5000), 2),
                    due_date=today - timedelta(days=random.randint(1, 15)),
                    is_paid=False,
                    created_by=admin_user.id
                )
                invoices.append(inv)
            
            # Current month invoices
            for i in range(5):
                due = today + timedelta(days=random.randint(1, 25))
                inv = Invoice(
                    company_id=company.id,
                    description=random.choice(invoice_descriptions),
                    amount=round(random.uniform(500, 8000), 2),
                    due_date=due,
                    is_paid=random.choice([True, False]),
                    created_by=admin_user.id,
                    file_url=None  # PDFs serão anexados manualmente pelo admin
                )
                invoices.append(inv)
            
            # Future invoices
            for i in range(3):
                inv = Invoice(
                    company_id=company.id,
                    description=random.choice(invoice_descriptions),
                    amount=round(random.uniform(1000, 10000), 2),
                    due_date=today + timedelta(days=random.randint(30, 90)),
                    is_paid=False,
                    created_by=admin_user.id
                )
                invoices.append(inv)
        
        for inv in invoices:
            db.add(inv)
        db.commit()
        
        print(f"✅ Created {len(invoices)} invoices")
        
        print("\n" + "="*50)
        print("🎉 Seed completed successfully!")
        print("="*50)
        print("\n📧 Login credentials:")
        print(f"   Super Admin: {settings.SUPERADMIN_EMAIL} / {settings.SUPERADMIN_PASSWORD}")
        print(f"   Admin: admin@example.com / admin123")
        print(f"   User (ACME): user@acme.com / user123")
        print(f"   User (TechStart): user@techstart.com / user123")
        
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
