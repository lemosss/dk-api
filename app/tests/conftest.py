import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import get_db
from app.models import Base, User, Company, RoleEnum
from app.core.security import get_password_hash

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database dependency override"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_company(db):
    """Create a test company"""
    company = Company(
        name="Test Company",
        cnpj="12.345.678/0001-90",
        email="test@company.com",
        phone="(11) 1234-5678",
        address="Test Address"
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@pytest.fixture
def superadmin_user(db):
    """Create a superadmin user"""
    user = User(
        email="superadmin@test.com",
        hashed_password=get_password_hash("super123"),
        name="Super Admin",
        role=RoleEnum.superadmin,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db):
    """Create an admin user"""
    user = User(
        email="admin@test.com",
        hashed_password=get_password_hash("admin123"),
        name="Admin User",
        role=RoleEnum.admin,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def regular_user(db, test_company):
    """Create a regular user"""
    user = User(
        email="user@test.com",
        hashed_password=get_password_hash("user123"),
        name="Regular User",
        role=RoleEnum.user,
        company_id=test_company.id,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def superadmin_token(client, superadmin_user):
    """Get authentication token for superadmin"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "superadmin@test.com", "password": "super123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_token(client, admin_user):
    """Get authentication token for admin"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@test.com", "password": "admin123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def user_token(client, regular_user):
    """Get authentication token for regular user"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "user@test.com", "password": "user123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def auth_headers_superadmin(superadmin_token):
    """Get authorization headers for superadmin"""
    return {"Authorization": f"Bearer {superadmin_token}"}


@pytest.fixture
def auth_headers_admin(admin_token):
    """Get authorization headers for admin"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def auth_headers_user(user_token):
    """Get authorization headers for regular user"""
    return {"Authorization": f"Bearer {user_token}"}
