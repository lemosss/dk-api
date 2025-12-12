from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.user.models import User, RoleEnum
from app.user.schemas import UserCreate, UserUpdate
from app.user.auth import hash_password, verify_password, create_access_token


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Authenticate user with email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuário inativo")
    return user


def create_user_token(user: User) -> str:
    """Create access token for user"""
    return create_access_token({"sub": str(user.id), "role": user.role.value})


def get_user_by_id(db: Session, user_id: int) -> User:
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_all_users(db: Session) -> list[User]:
    """Get all users"""
    return db.query(User).all()


def create_new_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user"""
    if get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        name=user_data.name,
        role=user_data.role,
        company_id=user_data.company_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_user_data(db: Session, user_id: int, user_data: UserUpdate) -> User:
    """Update user data"""
    user = get_user_by_id(db, user_id)
    for key, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user_by_id(db: Session, user_id: int) -> None:
    """Delete user by ID"""
    user = get_user_by_id(db, user_id)
    db.delete(user)
    db.commit()
