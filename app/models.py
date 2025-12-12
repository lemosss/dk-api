from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Date, Boolean, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class RoleEnum(str, enum.Enum):
    superadmin = "superadmin"
    admin = "admin"
    user = "user"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    role = Column(SQLEnum(RoleEnum), default=RoleEnum.user, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    company = relationship("Company", back_populates="users")


class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    cnpj = Column(String(20), unique=True, nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    users = relationship("User", back_populates="company")
    invoices = relationship("Invoice", back_populates="company")


class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    description = Column(String(500), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    due_date = Column(Date, nullable=False)
    file_url = Column(String(500), nullable=True)
    is_paid = Column(Boolean, default=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(String(1000), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    company = relationship("Company", back_populates="invoices")
    creator = relationship("User", foreign_keys=[created_by])
