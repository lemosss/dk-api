import pytest
from app.user.auth import hash_password, verify_password, create_access_token, decode_access_token


class TestPasswordHashing:
    """Test password hashing and verification"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "test_password123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "test_password123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "test_password123"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_hash_password_unicode(self):
        """Test password hashing with unicode characters"""
        password = "tëst_påsswörd123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_hash_password_truncates_long_passwords(self):
        """Test that passwords longer than 72 bytes are truncated"""
        long_password = "a" * 100
        hashed = hash_password(long_password)
        
        # Should verify with the original
        assert verify_password(long_password, hashed) is True
        
        # Should also verify with the truncated version
        truncated = "a" * 72
        assert verify_password(truncated, hashed) is True


class TestJWTTokens:
    """Test JWT token creation and decoding"""
    
    def test_create_access_token(self):
        """Test access token creation"""
        data = {"sub": "123", "role": "admin"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_access_token_valid(self):
        """Test decoding valid access token"""
        data = {"sub": "123", "role": "admin"}
        token = create_access_token(data)
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == "123"
        assert decoded["role"] == "admin"
        assert "exp" in decoded
    
    def test_decode_access_token_invalid(self):
        """Test decoding invalid access token"""
        invalid_token = "invalid.token.here"
        decoded = decode_access_token(invalid_token)
        
        assert decoded is None
    
    def test_decode_access_token_empty(self):
        """Test decoding empty token"""
        decoded = decode_access_token("")
        
        assert decoded is None
    
    def test_token_contains_expiration(self):
        """Test that token contains expiration time"""
        data = {"sub": "123"}
        token = create_access_token(data)
        decoded = decode_access_token(token)
        
        assert "exp" in decoded
        assert isinstance(decoded["exp"], int)
