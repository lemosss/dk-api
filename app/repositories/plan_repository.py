from typing import Optional
from sqlalchemy.orm import Session
from app.models.plan import Plan, PlanEnum
from app.repositories.base import BaseRepository


class PlanRepository(BaseRepository[Plan]):
    """Repository for Plan model"""

    def __init__(self, db: Session):
        super().__init__(Plan, db)

    def get_by_name(self, name: PlanEnum) -> Optional[Plan]:
        """Get plan by name"""
        return self.db.query(Plan).filter(Plan.name == name).first()

    def get_active_plans(self) -> list[Plan]:
        """Get all active plans"""
        return self.db.query(Plan).filter(Plan.is_active is True).all()

    def get_default_plan(self) -> Optional[Plan]:
        """Get the default (starter) plan"""
        return self.get_by_name(PlanEnum.starter)
