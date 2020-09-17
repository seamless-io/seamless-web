import datetime
import enum
import logging
import constants

from sqlalchemy import Column, Integer, DateTime, Text, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from core.models.base import base

from job_executor import scheduler


# IMPORTANT: use only this enum for populating Job.status column in the form of JobStatus.<status>.value
class JobStatus(enum.Enum):
    New = "NEW"
    Ok = "OK"
    Failed = "FAILED"
    Executing = "EXECUTING"


class Job(base):
    __tablename__ = 'jobs'
    __table_args__ = (UniqueConstraint('workspace_id',
                                       'name',
                                       name='job_names_must_be_unique_within_workspace'),
                      )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    workspace_id = Column(Integer, ForeignKey('workspaces.id'))
    job_template_id = Column(Integer, ForeignKey('job_templates.id', name='jobs_job_template_id_fkey'), nullable=True)
    user = relationship("User", back_populates="jobs")
    workspace = relationship("Workspace", back_populates="jobs")
    runs = relationship("JobRun", cascade="all,delete", back_populates="job",
                        order_by="desc(JobRun.created_at)", lazy='dynamic')
    parameters = relationship("JobParameter", cascade="all,delete",
                              back_populates="job", lazy='dynamic')
    template = relationship("JobTemplate", back_populates="jobs")

    name = Column(Text, nullable=False)
    # Alembic does not work very well with native postgres Enum type so the status column is Text
    status = Column(Text, default=JobStatus.New.value, nullable=False)
    # TODO: rename to `entrypoint_file`
    entrypoint = Column(Text, default=constants.DEFAULT_ENTRYPOINT)
    requirements = Column(Text, default=constants.DEFAULT_REQUIREMENTS)

    cron = Column(Text)
    aws_cron = Column(Text)
    human_cron = Column(Text)
    schedule_is_active = Column(Boolean)

    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    def schedule_job(self):
        if self.aws_cron:
            logging.info(f"Scheduling job: ({self.id}, {self.aws_cron}, active: {self.schedule_is_active})")
            scheduler.schedule(self.aws_cron, str(self.id), self.schedule_is_active)

    def get_parameters_as_dict(self):
        return {p.key: p.value for p in self.parameters}

    def __repr__(self):
        return '<Job %r %r %r>' % (self.id, self.name, self.aws_cron)
