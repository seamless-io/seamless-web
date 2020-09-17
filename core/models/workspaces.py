import enum
from dataclasses import dataclass

from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from core.models.base import base


class Plan(enum.Enum):
    Personal = "Personal"
    Startup = "Startup"
    Business = "Business"


@dataclass
class PlanLimits:
    jobs: int


PLAN_LIMITS_BY_TYPE = {
    Plan.Personal: PlanLimits(jobs=2),
    Plan.Startup: PlanLimits(jobs=7),
    Plan.Business: PlanLimits(jobs=30)
}


class Workspace(base):
    __tablename__ = 'workspaces'

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship("User", back_populates="owned_workspaces")
    jobs = relationship("Job", back_populates="workspace", lazy='dynamic')

    name = Column(Text, nullable=False)
    plan = Column(Text, nullable=False)
    subscription_is_active = Column(Boolean, nullable=False)

    def __repr__(self):
        return '<Workspace %r %r %r>' % (self.id, self.name, self.plan)
