import datetime
import enum

from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from core.models.base import base

# Without this import it's impossible to create `logs` relationship
from core.models.job_run_logs import JobRunLog  # pylint: disable=unused-import


# IMPORTANT: use only this enum for populating JobRun.type column in the form of JobRunType.<type>.value
class JobRunType(enum.Enum):
    RunButton = "RUN_BUTTON"
    Schedule = "SCHEDULE"


# IMPORTANT: use only this enum for populating JobRun.result column in the form of JobRunResult.<result>.value
class JobRunStatus(enum.Enum):
    Ok = "OK"
    Failed = "FAILED"
    Executing = "EXECUTING"


class JobRun(base):
    __tablename__ = 'job_runs'

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    job = relationship("Job", back_populates="runs")
    logs = relationship("JobRunLog", cascade="all,delete", back_populates="job_run", lazy='dynamic')

    type = Column(Text, nullable=False)
    status = Column(Text, default=JobRunStatus.Executing.value)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    def __repr__(self):
        return '<JobRun %r %r %r>' % (self.id, self.type, self.status)
