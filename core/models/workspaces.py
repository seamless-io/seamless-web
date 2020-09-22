import datetime
import enum
import uuid
from dataclasses import dataclass

from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

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

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<Workspace %r %r %r>' % (self.id, self.name, self.plan)


class InvitationStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"


class Invitation(base):
    __tablename__ = 'invitations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    user_id = Column(Integer)
    workspace_id = Column(Integer)

    status = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<Invitation(user_id={self.user_id}, workspace_id={self.workspace_id})>"
