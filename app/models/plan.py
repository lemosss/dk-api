from sqlalchemy import Column, Integer, String, DateTime, Boolean, Numeric, Enum as SQLEnum, func
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
from app.models.base import Base
import enum


class PlanEnum(str, enum.Enum):
    starter = "starter"
    profissional = "profissional"
    enterprise = "enterprise"


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(SQLEnum(PlanEnum), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)  # 0.00, 97.00, 297.00
    max_clients = Column(Integer, nullable=False)   # 1, 30, -1 (ilimitado)
    features = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    companies = relationship("Company", back_populates="plan")
