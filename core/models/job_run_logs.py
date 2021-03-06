from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from core.models.base import base


class JobRunLog(base):
    __tablename__ = 'job_run_logs'

    id = Column(Integer, primary_key=True)
    job_run_id = Column(Integer, ForeignKey('job_runs.id', ondelete='CASCADE'), nullable=False)
    job_run = relationship("JobRun", back_populates="logs")

    timestamp = Column(DateTime, nullable=False, index=True)
    message = Column(Text, nullable=False)

    def __repr__(self):
        return '<JobRunLog %r %r %r>' % (self.job_run_id, self.timestamp, self.message)
