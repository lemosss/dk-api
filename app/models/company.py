from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from app.models.base import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)

    # Identificador único para URL (slug) - ex: "acme", "techstart"
    company_key = Column(String(50), unique=True, nullable=False, index=True)

    name = Column(String(255), nullable=False)
    cnpj = Column(String(20), unique=True, nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)

    # Personalização visual
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), default="#3B82F6")  # Cor hex

    # Plano da empresa
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    plan = relationship("Plan", back_populates="companies")
    users = relationship("User", back_populates="company")
    invoices = relationship("Invoice", back_populates="company")

