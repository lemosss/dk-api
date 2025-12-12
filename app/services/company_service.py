from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.company import Company
from app.models.user import User
from app.models.invoice import Invoice
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
    
    def get_company_by_key(self, company_key: str) -> Company | None:
        """Get company by company_key"""
        return self.db.query(Company).filter(
            Company.company_key == company_key
        ).first()
    
    def create_company(self, company_data: CompanyCreate) -> Company:
        """Create a new company"""
        # Check if CNPJ already exists
        if self.company_repo.get_by_cnpj(company_data.cnpj):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CNPJ já cadastrado"
            )
        
        # Check if company_key already exists
        if self.get_company_by_key(company_data.company_key):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Identificador (company_key) já está em uso"
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
        
        # Check if company_key is being changed and already exists
        if company_data.company_key and company_data.company_key != company.company_key:
            existing = self.get_company_by_key(company_data.company_key)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Identificador (company_key) já está em uso"
                )
        
        update_data = company_data.model_dump(exclude_unset=True)
        return self.company_repo.update(company, update_data)
    
    def update_logo(self, company_id: int, logo_url: str) -> Company:
        """Update company logo"""
        company = self.get_company_by_id(company_id)
        company.logo_url = logo_url
        self.db.commit()
        self.db.refresh(company)
        return company
    
    def delete_company(self, company_id: int) -> bool:
        """Delete a company"""
        company = self.get_company_by_id(company_id)
        
        # Check if company has users
        users_count = self.db.query(User).filter(User.company_id == company_id).count()
        if users_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não é possível excluir. A empresa possui {users_count} usuário(s) vinculado(s)."
            )
        
        # Check if company has invoices
        invoices_count = self.db.query(Invoice).filter(Invoice.company_id == company_id).count()
        if invoices_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não é possível excluir. A empresa possui {invoices_count} fatura(s) vinculada(s)."
            )
        
        return self.company_repo.delete(company.id)
