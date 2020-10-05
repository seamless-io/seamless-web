import datetime

from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship

from core.models.base import base

PARAMETERS_LIMIT_PER_JOB = 30


class JobParameter(base):
    __tablename__ = 'job_parameters'
    __table_args__ = (
        # A single Job cannot have different Parameters with the same Key
        UniqueConstraint('job_id', 'key'),
    )

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    job = relationship("Job", back_populates="parameters")

    key = Column(Text, nullable=False)
    value = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    def __repr__(self):
        return '<JobParameter %r %r %r>' % (self.id, self.key, self.value)
