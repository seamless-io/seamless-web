import datetime
import enum

from sqlalchemy import Column, Integer, DateTime, Text, Enum, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from core.db.models.base import base


class JobStatus(enum.Enum):
    New = 1
    Ok = 2
    Failed = 3
    Executing = 3


class Job(base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="jobs")

    name = Column(Text)
    schedule = Column(Text)
    schedule_is_active = Column(Boolean)
    status = Column(Enum(JobStatus))
    created_at = Column(DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<Job %r %r %r>' % (self.id, self.name, self.schedule)
