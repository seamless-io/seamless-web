import datetime
import enum
import uuid

from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.models.base import base


class Workspace(base):
    __tablename__ = 'workspaces'

    id = Column(Integer, primary_key=True)

    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="owned_workspaces")

    plan_id = Column(Integer, ForeignKey('workspace_plans.id'))
    plan = relationship("WorkspacePlan", back_populates="workspace")

    jobs = relationship("Job", back_populates="workspace", lazy='dynamic')

    name = Column(Text, nullable=False)
    personal = Column(Boolean)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<Workspace %r %r %r>' % (self.id, self.name, self.plan)


class InvitationStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"


class Invitation(base):
    __tablename__ = 'invitations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    user_email = Column(Text, nullable=False)
    workspace_id = Column(Integer, nullable=False)

    status = Column(Text, nullable=False, default=InvitationStatus.pending.value)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<Invitation(user_id={self.user_id}, workspace_id={self.workspace_id})>"
