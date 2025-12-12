import pytest
from app.models import RoleEnum


class TestUserEndpoints:
    """Test user management endpoints"""
    
    def test_list_users_as_superadmin(self, client, auth_headers_superadmin, superadmin_user):
        """Test listing users as superadmin"""
        response = client.get("/api/v1/users/", headers=auth_headers_superadmin)
        
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 1
    
    def test_list_users_as_admin_forbidden(self, client, auth_headers_admin):
        """Test listing users as admin (should be forbidden)"""
        response = client.get("/api/v1/users/", headers=auth_headers_admin)
        
        assert response.status_code == 403
    
    def test_list_users_as_user_forbidden(self, client, auth_headers_user):
        """Test listing users as regular user (should be forbidden)"""
        response = client.get("/api/v1/users/", headers=auth_headers_user)
        
        assert response.status_code == 403
    
    def test_get_user_by_id(self, client, auth_headers_superadmin, admin_user):
        """Test getting user by ID"""
        response = client.get(
            f"/api/v1/users/{admin_user.id}",
            headers=auth_headers_superadmin
        )
        
        assert response.status_code == 200
        user = response.json()
        assert user["id"] == admin_user.id
        assert user["email"] == admin_user.email
    
    def test_get_user_not_found(self, client, auth_headers_superadmin):
        """Test getting nonexistent user"""
        response = client.get("/api/v1/users/9999", headers=auth_headers_superadmin)
        
        assert response.status_code == 404
    
    def test_create_user(self, client, auth_headers_superadmin):
        """Test creating a new user"""
        user_data = {
            "email": "newuser@test.com",
            "password": "password123",
            "name": "New User",
            "role": "user"
        }
        
        response = client.post(
            "/api/v1/users/",
            json=user_data,
            headers=auth_headers_superadmin
        )
        
        assert response.status_code == 201
        user = response.json()
        assert user["email"] == "newuser@test.com"
        assert user["name"] == "New User"
        assert "id" in user
    
    def test_create_user_duplicate_email(self, client, auth_headers_superadmin, admin_user):
        """Test creating user with duplicate email"""
        user_data = {
            "email": admin_user.email,
            "password": "password123",
            "name": "Duplicate"
        }
        
        response = client.post(
            "/api/v1/users/",
            json=user_data,
            headers=auth_headers_superadmin
        )
        
        assert response.status_code == 400
        assert "já cadastrado" in response.json()["detail"].lower()
    
    def test_create_user_as_admin_forbidden(self, client, auth_headers_admin):
        """Test creating user as admin (should be forbidden)"""
        user_data = {
            "email": "test@test.com",
            "password": "password123"
        }
        
        response = client.post(
            "/api/v1/users/",
            json=user_data,
            headers=auth_headers_admin
        )
        
        assert response.status_code == 403
    
    def test_update_user(self, client, auth_headers_superadmin, admin_user):
        """Test updating a user"""
        update_data = {"name": "Updated Name"}
        
        response = client.put(
            f"/api/v1/users/{admin_user.id}",
            json=update_data,
            headers=auth_headers_superadmin
        )
        
        assert response.status_code == 200
        user = response.json()
        assert user["name"] == "Updated Name"
    
    def test_update_user_not_found(self, client, auth_headers_superadmin):
        """Test updating nonexistent user"""
        response = client.put(
            "/api/v1/users/9999",
            json={"name": "Test"},
            headers=auth_headers_superadmin
        )
        
        assert response.status_code == 404
    
    def test_delete_user(self, client, auth_headers_superadmin, db):
        """Test deleting a user"""
        # Create a user to delete
        from app.models import User
        from app.core.security import get_password_hash
        
        user = User(
            email="todelete@test.com",
            hashed_password=get_password_hash("password"),
            role=RoleEnum.user
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        response = client.delete(
            f"/api/v1/users/{user.id}",
            headers=auth_headers_superadmin
        )
        
        assert response.status_code == 204
    
    def test_delete_user_not_found(self, client, auth_headers_superadmin):
        """Test deleting nonexistent user"""
        response = client.delete(
            "/api/v1/users/9999",
            headers=auth_headers_superadmin
        )
        
        assert response.status_code == 404
