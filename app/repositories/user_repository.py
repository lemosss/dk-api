from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User, RoleEnum
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model"""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_role(self, role: RoleEnum) -> list[User]:
        """Get all users with specific role"""
        return self.db.query(User).filter(User.role == role).all()
    
    def get_active_users(self) -> list[User]:
        """Get all active users"""
        return self.db.query(User).filter(User.is_active == True).all()
    
    def get_by_company(self, company_id: int) -> list[User]:
        """Get all users from a specific company"""
        return self.db.query(User).filter(User.company_id == company_id).all()
