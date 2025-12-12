import pytest
from app.models import User, RoleEnum
from app.core.security import get_password_hash


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_login_success(self, client, superadmin_user):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "superadmin@test.com", "password": "super123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_wrong_password(self, client, superadmin_user):
        """Test login with wrong password"""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "superadmin@test.com", "password": "wrongpassword"}
        )
        
        assert response.status_code == 401
        assert "Credenciais inválidas" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user"""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "nonexistent@test.com", "password": "password"}
        )
        
        assert response.status_code == 401
    
    def test_login_inactive_user(self, client, db):
        """Test login with inactive user"""
        # Create inactive user
        user = User(
            email="inactive@test.com",
            hashed_password=get_password_hash("password123"),
            name="Inactive User",
            role=RoleEnum.user,
            is_active=False
        )
        db.add(user)
        db.commit()
        
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "inactive@test.com", "password": "password123"}
        )
        
        assert response.status_code == 403
        assert "inativo" in response.json()["detail"].lower()
    
    def test_get_current_user(self, client, auth_headers_superadmin, superadmin_user):
        """Test getting current user info"""
        response = client.get("/api/v1/auth/me", headers=auth_headers_superadmin)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == superadmin_user.email
        assert data["role"] == superadmin_user.role.value
        assert "id" in data
    
    def test_get_current_user_no_token(self, client):
        """Test getting current user without token"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        assert response.status_code == 401
    
    def test_get_current_user_expired_token(self, client, db, superadmin_user):
        """Test with malformed token"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer malformed"}
        )
        
        assert response.status_code == 401
