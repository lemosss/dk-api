from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.plan import Plan, PlanEnum
from app.models.company import Company
from app.models.user import User
from app.repositories.plan_repository import PlanRepository


class PlanService:
    """Service for plan management and validation"""

    def __init__(self, db: Session):
        self.db = db
        self.plan_repo = PlanRepository(db)

    def get_all_plans(self) -> list[Plan]:
        """Get all active plans"""
        return self.plan_repo.get_active_plans()

    def get_plan_by_id(self, plan_id: int) -> Plan:
        """Get plan by ID"""
        plan = self.plan_repo.get(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plano não encontrado"
            )
        return plan

    def get_default_plan(self) -> Plan:
        """Get the default (starter) plan"""
        plan = self.plan_repo.get_default_plan()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Plano padrão não configurado"
            )
        return plan

    def get_company_client_count(self, company_id: int) -> int:
        """Count the number of clients (users) in a company"""
        return self.db.query(User).filter(
            User.company_id == company_id,
            User.is_active is True
        ).count()

    def check_client_limit(self, company_id: int) -> bool:
        """
        Check if company can add more clients based on plan limit.
        Returns True if can add, False if limit reached.
        """
        company = self.db.query(Company).filter(
            Company.id == company_id
        ).first()

        if not company:
            return False

        if not company.plan_id:
            # Se não tem plano, assume starter (1 cliente)
            plan = self.get_default_plan()
        else:
            plan = self.get_plan_by_id(company.plan_id)

        # -1 significa ilimitado
        if plan.max_clients == -1:
            return True

        current_count = self.get_company_client_count(company_id)
        return current_count < plan.max_clients

    def get_upgrade_options(self, company_id: int) -> list[Plan]:
        """Get plans that are upgrades from current company plan"""
        company = self.db.query(Company).filter(
            Company.id == company_id
        ).first()

        if not company or not company.plan_id:
            current_plan = self.get_default_plan()
        else:
            current_plan = self.get_plan_by_id(company.plan_id)

        all_plans = self.get_all_plans()

        # Filtrar planos com max_clients maior que o atual
        # ou ilimitado (-1)
        upgrade_plans = []
        for plan in all_plans:
            if plan.id == current_plan.id:
                continue
            if plan.max_clients == -1:
                upgrade_plans.append(plan)
            elif current_plan.max_clients != -1:
                if plan.max_clients > current_plan.max_clients:
                    upgrade_plans.append(plan)

        return upgrade_plans

    def validate_client_limit_or_raise(self, company_id: int) -> None:
        """
        Validate if company can add more clients.
        Raises HTTP 402 if limit reached.
        """
        if not self.check_client_limit(company_id):
            upgrade_options = self.get_upgrade_options(company_id)
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "client_limit_reached",
                    "message": "Limite de clientes atingido para o seu plano",
                    "upgrade_required": True,
                    "upgrade_options": [
                        {
                            "id": p.id,
                            "name": p.display_name,
                            "price": float(p.price),
                            "max_clients": p.max_clients
                        }
                        for p in upgrade_options
                    ]
                }
            )
