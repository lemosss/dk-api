from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.repositories.user_repository import UserRepository


class UserService:
    """Service for user management operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def get_all_users(self) -> list[User]:
        """Get all users"""
        return self.user_repo.get_all()
    
    def get_user_by_id(self, user_id: int) -> User:
        """Get user by ID"""
        user = self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        return user
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if email already exists
        if self.user_repo.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
        
        # Create user
        user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            name=user_data.name,
            role=user_data.role,
            company_id=user_data.company_id
        )
        return self.user_repo.create(user)
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update an existing user"""
        user = self.get_user_by_id(user_id)
        
        # Check if email is being changed and already exists
        if user_data.email and user_data.email != user.email:
            existing = self.user_repo.get_by_email(user_data.email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já cadastrado"
                )
        
        update_data = user_data.model_dump(exclude_unset=True)
        return self.user_repo.update(user, update_data)
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        user = self.get_user_by_id(user_id)
        return self.user_repo.delete(user.id)
