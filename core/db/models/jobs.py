import datetime
import enum

from sqlalchemy import Column, Integer, DateTime, Text, Enum, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from core.db.models.base import base


# IMPORTANT: use only this enum for populating Job.status column in the form of JobStatus.<status>.value
class JobStatus(enum.Enum):
    New = "New"
    Ok = "Ok"
    Failed = "Failed"
    Executing = "Executing"


class Job(base):
    __tablename__ = 'jobs'
    __table_args__ = (UniqueConstraint('user_id',
                                       'name',
                                       name='job_names_must_be_unique_within_user'),
                      )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="jobs")

    name = Column(Text, nullable=False)
    # Alembic does not work very well with native postgres Enum type so the status column is Text
    status = Column(Text, default=JobStatus.New.value, nullable=False)
    schedule = Column(Text)
    schedule_is_active = Column(Boolean)
    created_at = Column(DateTime, default=datetime.datetime.now(), nullable=False)

    def __repr__(self):
        return '<Job %r %r %r>' % (self.id, self.name, self.schedule)
