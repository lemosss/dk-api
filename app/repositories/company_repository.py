from typing import Optional
from sqlalchemy.orm import Session
from app.models.company import Company
from app.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    """Repository for Company model"""
    
    def __init__(self, db: Session):
        super().__init__(Company, db)
    
    def get_by_cnpj(self, cnpj: str) -> Optional[Company]:
        """Get company by CNPJ"""
        return self.db.query(Company).filter(Company.cnpj == cnpj).first()
    
    def get_active_companies(self) -> list[Company]:
        """Get all active companies"""
        return self.db.query(Company).filter(Company.is_active == True).all()
