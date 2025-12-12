from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.repositories.company_repository import CompanyRepository


class CompanyService:
    """Service for company management operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.company_repo = CompanyRepository(db)
    
    def get_all_companies(self) -> list[Company]:
        """Get all companies"""
        return self.company_repo.get_all()
    
    def get_company_by_id(self, company_id: int) -> Company:
        """Get company by ID"""
        company = self.company_repo.get(company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empresa não encontrada"
            )
        return company
    
    def create_company(self, company_data: CompanyCreate) -> Company:
        """Create a new company"""
        # Check if CNPJ already exists
        if self.company_repo.get_by_cnpj(company_data.cnpj):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CNPJ já cadastrado"
            )
        
        company = Company(**company_data.model_dump())
        return self.company_repo.create(company)
    
    def update_company(self, company_id: int, company_data: CompanyUpdate) -> Company:
        """Update an existing company"""
        company = self.get_company_by_id(company_id)
        
        # Check if CNPJ is being changed and already exists
        if company_data.cnpj and company_data.cnpj != company.cnpj:
            existing = self.company_repo.get_by_cnpj(company_data.cnpj)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CNPJ já cadastrado"
                )
        
        update_data = company_data.model_dump(exclude_unset=True)
        return self.company_repo.update(company, update_data)
    
    def delete_company(self, company_id: int) -> bool:
        """Delete a company"""
        company = self.get_company_by_id(company_id)
        return self.company_repo.delete(company.id)
