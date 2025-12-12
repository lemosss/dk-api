from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User, RoleEnum
from app.models.company import Company
from app.core.security import get_password_hash, create_access_token
from app.repositories.user_repository import UserRepository
from app.repositories.company_repository import CompanyRepository
from app.services.plan_service import PlanService
from app.schemas.plan import RegisterRequest, RegisterResponse
from app.schemas.user import UserOut


class RegistrationService:
    """Service for self-registration of companies and admin users"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.company_repo = CompanyRepository(db)
        self.plan_service = PlanService(db)

    def register(self, data: RegisterRequest) -> RegisterResponse:
        """
        Register a new company with an admin user.
        This is a public endpoint for self-registration.
        """
        # 1. Validate email is unique
        existing_user = self.user_repo.get_by_email(data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )

        # 2. Validate company_key is unique
        existing_company = self.db.query(Company).filter(
            Company.company_key == data.company_key
        ).first()
        if existing_company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Identificador da empresa já está em uso"
            )

        # 3. Validate CNPJ is unique
        existing_cnpj = self.company_repo.get_by_cnpj(data.cnpj)
        if existing_cnpj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CNPJ já cadastrado"
            )

        # 4. Get plan (default to starter if not specified)
        if data.plan_id:
            plan = self.plan_service.get_plan_by_id(data.plan_id)
        else:
            plan = self.plan_service.get_default_plan()

        # 5. Create Company
        company = Company(
            name=data.company_name,
            company_key=data.company_key,
            cnpj=data.cnpj,
            plan_id=plan.id
        )
        self.db.add(company)
        self.db.flush()  # Get the company ID without committing

        # 6. Create User as admin of the company
        user = User(
            email=data.email,
            hashed_password=get_password_hash(data.password),
            name=data.name,
            role=RoleEnum.admin,
            company_id=company.id,
            is_active=True
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        self.db.refresh(company)

        # 7. Create JWT token
        token_data = {
            "sub": str(user.id),
            "role": user.role.value
        }
        access_token = create_access_token(token_data)

        # 8. Return response
        return RegisterResponse(
            access_token=access_token,
            token_type="bearer",
            company_key=company.company_key,
            user=UserOut.model_validate(user)
        )
