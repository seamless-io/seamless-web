import datetime
import enum

from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from backend.db.models.base import base


# IMPORTANT: use only this enum for populating JobRun.type column in the form of JobRunType.<type>.value
class JobRunType(enum.Enum):
    RunButton = "RunButton"
    Schedule = "Schedule"


# IMPORTANT: use only this enum for populating JobRun.result column in the form of JobRunResult.<result>.value
class JobRunResult(enum.Enum):
    Ok = "OK"
    Failed = "FAILED"
    Executing = "EXECUTING"


class JobRun(base):
    __tablename__ = 'job_runs'

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    job = relationship("Job", back_populates="runs")
    logs = relationship("JobRunLog", back_populates="job_run")

    type = Column(Text, nullable=False)
    status = Column(Text, default=JobRunResult.Executing.value, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(), nullable=False)

    def __repr__(self):
        return '<JobRun %r %r %r>' % (self.id, self.type, self.result)
