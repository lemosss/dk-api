import pytest
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token
)


class TestPasswordHashing:
    """Test password hashing functions"""
    
    def test_get_password_hash(self):
        """Test password hashing"""
        password = "test123"
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "test123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "test123"
        wrong_password = "wrong123"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_password_hash_different_each_time(self):
        """Test that same password produces different hashes"""
        password = "test123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTToken:
    """Test JWT token functions"""
    
    def test_create_access_token(self):
        """Test token creation"""
        data = {"sub": "123", "role": "user"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_access_token_valid(self):
        """Test decoding valid token"""
        data = {"sub": "123", "role": "user"}
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == "123"
        assert decoded["role"] == "user"
        assert "exp" in decoded
    
    def test_decode_access_token_invalid(self):
        """Test decoding invalid token"""
        invalid_token = "invalid.token.here"
        
        decoded = decode_access_token(invalid_token)
        
        assert decoded is None
    
    def test_decode_access_token_empty(self):
        """Test decoding empty token"""
        decoded = decode_access_token("")
        
        assert decoded is None
    
    def test_token_contains_expiration(self):
        """Test that token contains expiration"""
        data = {"sub": "123"}
        token = create_access_token(data)
        decoded = decode_access_token(token)
        
        assert "exp" in decoded
        assert isinstance(decoded["exp"], int)
