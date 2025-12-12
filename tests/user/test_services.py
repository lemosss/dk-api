import pytest
from fastapi import HTTPException
from app.user.models import User, RoleEnum
from app.user.schemas import UserCreate, UserUpdate
from app.user import services


class TestAuthenticationServices:
    """Test user authentication services"""
    
    def test_authenticate_user_success(self, db_session, test_user):
        """Test successful user authentication"""
        user = services.authenticate_user(db_session, test_user.email, "password123")
        
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
    
    def test_authenticate_user_wrong_password(self, db_session, test_user):
        """Test authentication with wrong password"""
        with pytest.raises(HTTPException) as exc_info:
            services.authenticate_user(db_session, test_user.email, "wrong_password")
        
        assert exc_info.value.status_code == 401
        assert "Credenciais inválidas" in exc_info.value.detail
    
    def test_authenticate_user_nonexistent(self, db_session):
        """Test authentication with nonexistent user"""
        with pytest.raises(HTTPException) as exc_info:
            services.authenticate_user(db_session, "nonexistent@test.com", "password123")
        
        assert exc_info.value.status_code == 401
    
    def test_authenticate_user_inactive(self, db_session, test_user):
        """Test authentication with inactive user"""
        test_user.is_active = False
        db_session.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            services.authenticate_user(db_session, test_user.email, "password123")
        
        assert exc_info.value.status_code == 403
        assert "inativo" in exc_info.value.detail.lower()
    
    def test_create_user_token(self, test_user):
        """Test creating user token"""
        token = services.create_user_token(test_user)
        
        assert isinstance(token, str)
        assert len(token) > 0


class TestUserCRUD:
    """Test user CRUD operations"""
    
    def test_get_user_by_id_exists(self, db_session, test_user):
        """Test getting existing user by ID"""
        user = services.get_user_by_id(db_session, test_user.id)
        
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
    
    def test_get_user_by_id_not_exists(self, db_session):
        """Test getting nonexistent user by ID"""
        with pytest.raises(HTTPException) as exc_info:
            services.get_user_by_id(db_session, 99999)
        
        assert exc_info.value.status_code == 404
    
    def test_get_user_by_email_exists(self, db_session, test_user):
        """Test getting existing user by email"""
        user = services.get_user_by_email(db_session, test_user.email)
        
        assert user is not None
        assert user.email == test_user.email
    
    def test_get_user_by_email_not_exists(self, db_session):
        """Test getting nonexistent user by email"""
        user = services.get_user_by_email(db_session, "nonexistent@test.com")
        
        assert user is None
    
    def test_get_all_users(self, db_session, test_user, test_admin, test_superadmin):
        """Test getting all users"""
        users = services.get_all_users(db_session)
        
        assert len(users) >= 3
        emails = [u.email for u in users]
        assert test_user.email in emails
        assert test_admin.email in emails
        assert test_superadmin.email in emails
    
    def test_create_new_user(self, db_session, test_company):
        """Test creating new user"""
        user_data = UserCreate(
            email="newuser@test.com",
            password="newpassword123",
            name="New User",
            role=RoleEnum.user,
            company_id=test_company.id
        )
        
        user = services.create_new_user(db_session, user_data)
        
        assert user is not None
        assert user.email == "newuser@test.com"
        assert user.name == "New User"
        assert user.role == RoleEnum.user
        assert user.company_id == test_company.id
        assert user.hashed_password != "newpassword123"  # Should be hashed
    
    def test_create_new_user_duplicate_email(self, db_session, test_user):
        """Test creating user with duplicate email"""
        user_data = UserCreate(
            email=test_user.email,
            password="password123",
            name="Duplicate"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            services.create_new_user(db_session, user_data)
        
        assert exc_info.value.status_code == 400
        assert "já cadastrado" in exc_info.value.detail.lower()
    
    def test_update_user_data(self, db_session, test_user):
        """Test updating user data"""
        update_data = UserUpdate(
            name="Updated Name",
            email="updated@test.com"
        )
        
        user = services.update_user_data(db_session, test_user.id, update_data)
        
        assert user.name == "Updated Name"
        assert user.email == "updated@test.com"
    
    def test_update_user_partial(self, db_session, test_user):
        """Test partial user update"""
        original_email = test_user.email
        update_data = UserUpdate(name="Only Name Changed")
        
        user = services.update_user_data(db_session, test_user.id, update_data)
        
        assert user.name == "Only Name Changed"
        assert user.email == original_email  # Should remain unchanged
    
    def test_delete_user_by_id(self, db_session, test_user):
        """Test deleting user"""
        user_id = test_user.id
        services.delete_user_by_id(db_session, user_id)
        
        # Verify user was deleted
        user = db_session.query(User).filter(User.id == user_id).first()
        assert user is None
    
    def test_delete_user_not_exists(self, db_session):
        """Test deleting nonexistent user"""
        with pytest.raises(HTTPException) as exc_info:
            services.delete_user_by_id(db_session, 99999)
        
        assert exc_info.value.status_code == 404
