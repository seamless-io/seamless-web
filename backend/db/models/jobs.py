import datetime
import enum

from sqlalchemy import Column, Integer, DateTime, Text, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from backend.db.models.base import base
from job_executor import scheduler


# IMPORTANT: use only this enum for populating Job.status column in the form of JobStatus.<status>.value
class JobStatus(enum.Enum):
    New = "NEW"
    Ok = "OK"
    Failed = "FAILED"
    Executing = "EXECUTING"


class Job(base):
    __tablename__ = 'jobs'
    __table_args__ = (UniqueConstraint('user_id',
                                       'name',
                                       name='job_names_must_be_unique_within_user'),
                      )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="jobs")
    runs = relationship("JobRun", back_populates="job")

    name = Column(Text, nullable=False)
    # Alembic does not work very well with native postgres Enum type so the status column is Text
    status = Column(Text, default=JobStatus.New.value, nullable=False)
    schedule = Column(Text)
    schedule_is_active = Column(Boolean)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    def schedule_job(self):
        if self.schedule and self.schedule_is_active:
            scheduler.schedule(self.schedule, str(self.id))

    def get_sorted_job_runs(self):
        return sorted(self.runs, key=lambda o: o.created_at, reverse=True)

    def __repr__(self):
        return '<Job %r %r %r>' % (self.id, self.name, self.schedule)
