from sqlalchemy import Column, Integer, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from core.models.base import base


class Workspace(base):
    __tablename__ = 'workspaces'

    id = Column(Integer, primary_key=True)

    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    owner = relationship('User')

    name = Column(Text, nullable=False, default="Personal")
    personal = Column(Boolean, default=True)

    jobs = relationship('Job', back_populates='workspace', passive_deletes=True)

    def __repr__(self):
        return f"<Workspace(id={self.id}, owner_id={self.owner_id})>"
