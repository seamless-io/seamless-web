import datetime

from sqlalchemy import Column, Integer, DateTime, Text, LargeBinary
from sqlalchemy.orm import relationship

from core.models.base import base


class JobTemplate(base):
    __tablename__ = 'job_templates'

    id = Column(Integer, primary_key=True)
    jobs = relationship("Job", cascade="all,delete", back_populates="template", lazy='dynamic')

    name = Column(Text, nullable=False, unique=True, index=True)
    short_description = Column(Text, nullable=False)
    long_description_url = Column(Text, nullable=False)
    tags = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    @staticmethod
    def get_template_from_name(name, session):
        return session.query(JobTemplate).filter(JobTemplate.name == name).one_or_none()

    def __repr__(self):
        return '<JobTemplate %r %r>' % (self.id, self.name)
