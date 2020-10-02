import datetime
import enum
from dataclasses import dataclass

from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from core.models.base import base


class WorkspacePlanSize(enum.Enum):
    S = 'S'
    M = 'M'
    L = 'L'


@dataclass
class PlanLimits:
    jobs: int


PLAN_LIMITS_BY_TYPE = {
    WorkspacePlanSize.S: PlanLimits(jobs=2),
    WorkspacePlanSize.M: PlanLimits(jobs=7),
    WorkspacePlanSize.L: PlanLimits(jobs=30)
}


class WorkspacePlan(base):
    __tablename__ = 'workspace_plans'

    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey('subscriptions.id'))
    workspace_id = Column(Integer, ForeignKey('workspaces.id'))

    subscription = relationship("Subscription")
    workspace = relationship("Workspace", back_populates="plan")

    size = Column(Text, nullable=False)  # Use only values from WorkspacePlanLevel

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<Plan %r %r>' % (self.id, self.name)
