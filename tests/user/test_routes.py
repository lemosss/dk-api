import pytest
from app.user.models import RoleEnum


class TestAuthenticationRoutes:
    """Test authentication routes"""
    
    @pytest.mark.parametrize("email,password,expected_status", [
        ("superadmin@test.com", "password123", 200),
        ("admin@test.com", "password123", 200),
        ("user@test.com", "password123", 200),
        ("wrong@test.com", "password123", 401),
        ("superadmin@test.com", "wrong_password", 401),
    ])
    def test_login_various_credentials(self, client, test_superadmin, test_admin, test_user, email, password, expected_status):
        """Test login with various credential combinations (parameterized)"""
        response = client.post(
            "/api/auth/login",
            data={"username": email, "password": password}
        )
        
        assert response.status_code == expected_status
        
        if expected_status == 200:
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
    
    def test_login_success_superadmin(self, client, test_superadmin):
        """Test successful login as superadmin"""
        response = client.post(
            "/api/auth/login",
            data={"username": test_superadmin.email, "password": "password123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_success_admin(self, client, test_admin):
        """Test successful login as admin"""
        response = client.post(
            "/api/auth/login",
            data={"username": test_admin.email, "password": "password123"}
        )
        
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_login_success_user(self, client, test_user):
        """Test successful login as regular user"""
        response = client.post(
            "/api/auth/login",
            data={"username": test_user.email, "password": "password123"}
        )
        
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/auth/login",
            data={"username": test_user.email, "password": "wrong_password"}
        )
        
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user"""
        response = client.post(
            "/api/auth/login",
            data={"username": "nonexistent@test.com", "password": "password123"}
        )
        
        assert response.status_code == 401
    
    def test_login_inactive_user(self, client, test_user, db_session):
        """Test login with inactive user"""
        test_user.is_active = False
        db_session.commit()
        
        response = client.post(
            "/api/auth/login",
            data={"username": test_user.email, "password": "password123"}
        )
        
        assert response.status_code == 403
    
    def test_get_current_user(self, client, superadmin_token, test_superadmin):
        """Test getting current user info"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {superadmin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_superadmin.email
        assert data["role"] == RoleEnum.superadmin.value
    
    def test_get_current_user_no_token(self, client):
        """Test getting current user without token"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401


class TestUserRoutes:
    """Test user management routes"""
    
    def test_list_users_as_superadmin(self, client, superadmin_token, test_user, test_admin):
        """Test listing users as superadmin"""
        response = client.get(
            "/api/users/",
            headers={"Authorization": f"Bearer {superadmin_token}"}
        )
        
        assert response.status_code == 200
        users = response.json()
        assert len(users) >= 3  # At least superadmin, admin, user
    
    def test_list_users_as_admin(self, client, admin_token):
        """Test listing users as admin"""
        response = client.get(
            "/api/users/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
    
    def test_list_users_as_user(self, client, user_token):
        """Test listing users as regular user (should fail)"""
        response = client.get(
            "/api/users/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 403
    
    def test_create_user_as_superadmin(self, client, superadmin_token, test_company):
        """Test creating user as superadmin"""
        user_data = {
            "email": "newuser@test.com",
            "password": "password123",
            "name": "New User",
            "role": RoleEnum.user.value,
            "company_id": test_company.id
        }
        
        response = client.post(
            "/api/users/",
            json=user_data,
            headers={"Authorization": f"Bearer {superadmin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@test.com"
        assert data["name"] == "New User"
    
    def test_create_user_as_admin(self, client, admin_token):
        """Test creating user as admin (should fail)"""
        user_data = {
            "email": "newuser2@test.com",
            "password": "password123",
            "name": "New User 2"
        }
        
        response = client.post(
            "/api/users/",
            json=user_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 403
    
    def test_create_user_duplicate_email(self, client, superadmin_token, test_user):
        """Test creating user with duplicate email"""
        user_data = {
            "email": test_user.email,
            "password": "password123",
            "name": "Duplicate"
        }
        
        response = client.post(
            "/api/users/",
            json=user_data,
            headers={"Authorization": f"Bearer {superadmin_token}"}
        )
        
        assert response.status_code == 400
    
    def test_update_user_as_superadmin(self, client, superadmin_token, test_user):
        """Test updating user as superadmin"""
        update_data = {
            "name": "Updated Name"
        }
        
        response = client.put(
            f"/api/users/{test_user.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {superadmin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
    
    def test_update_user_as_admin(self, client, admin_token, test_user):
        """Test updating user as admin (should fail)"""
        update_data = {
            "name": "Updated Name"
        }
        
        response = client.put(
            f"/api/users/{test_user.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 403
    
    def test_delete_user_as_superadmin(self, client, superadmin_token, test_user):
        """Test deleting user as superadmin"""
        response = client.delete(
            f"/api/users/{test_user.id}",
            headers={"Authorization": f"Bearer {superadmin_token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["ok"] is True
    
    def test_delete_user_as_admin(self, client, admin_token, test_user):
        """Test deleting user as admin (should fail)"""
        response = client.delete(
            f"/api/users/{test_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 403
    
    def test_delete_nonexistent_user(self, client, superadmin_token):
        """Test deleting nonexistent user"""
        response = client.delete(
            "/api/users/99999",
            headers={"Authorization": f"Bearer {superadmin_token}"}
        )
        
        assert response.status_code == 404
