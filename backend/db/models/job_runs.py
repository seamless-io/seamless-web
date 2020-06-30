import datetime
import enum

from sqlalchemy import Column, Integer, DateTime, Text, Enum, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from backend.db.models.base import base


# IMPORTANT: use only this enum for populating JobRun.type column in the form of JobRunType.<type>.value
class JobRunType(enum.Enum):
    RunButton = "RunButton"
    Schedule = "Schedule"


# IMPORTANT: use only this enum for populating JobRun.result column in the form of JobRunResult.<result>.value
class JobRunResult(enum.Enum):
    Ok = "Ok"
    Failed = "Failed"
    Executing = "Executing"


class JobRun(base):
    __tablename__ = 'job_runs'

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    job = relationship("Job", back_populates="runs")

    type = Column(Text, nullable=False)
    result = Column(Text, default=JobRunResult.Executing.value, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(), nullable=False)

    def __repr__(self):
        return '<Job %r %r %r>' % (self.id, self.name, self.schedule)