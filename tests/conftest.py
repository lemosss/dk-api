import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.common.database import Base, get_db
from app.main import app
from app.user.models import User, RoleEnum
from app.order.models import Company, Invoice
from app.user.auth import hash_password
from datetime import date, timedelta


# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_company(db_session):
    """Create a test company"""
    company = Company(
        name="Test Company",
        cnpj="12.345.678/0001-90",
        email="test@company.com",
        phone="(11) 1234-5678",
        address="Test Address, 123"
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


@pytest.fixture
def test_superadmin(db_session):
    """Create a test superadmin user"""
    user = User(
        email="superadmin@test.com",
        hashed_password=hash_password("password123"),
        name="Super Admin",
        role=RoleEnum.superadmin,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session):
    """Create a test admin user"""
    user = User(
        email="admin@test.com",
        hashed_password=hash_password("password123"),
        name="Admin User",
        role=RoleEnum.admin,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user(db_session, test_company):
    """Create a test regular user"""
    user = User(
        email="user@test.com",
        hashed_password=hash_password("password123"),
        name="Regular User",
        role=RoleEnum.user,
        company_id=test_company.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_invoice(db_session, test_company, test_admin):
    """Create a test invoice"""
    invoice = Invoice(
        company_id=test_company.id,
        description="Test Invoice",
        amount=1000.00,
        due_date=date.today() + timedelta(days=7),
        is_paid=False,
        created_by=test_admin.id
    )
    db_session.add(invoice)
    db_session.commit()
    db_session.refresh(invoice)
    return invoice


@pytest.fixture
def superadmin_token(client, test_superadmin):
    """Get authentication token for superadmin"""
    response = client.post(
        "/api/auth/login",
        data={"username": test_superadmin.email, "password": "password123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_token(client, test_admin):
    """Get authentication token for admin"""
    response = client.post(
        "/api/auth/login",
        data={"username": test_admin.email, "password": "password123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def user_token(client, test_user):
    """Get authentication token for regular user"""
    response = client.post(
        "/api/auth/login",
        data={"username": test_user.email, "password": "password123"}
    )
    return response.json()["access_token"]
