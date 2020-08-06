import datetime
import enum
import logging
import config

from sqlalchemy import Column, Integer, DateTime, Text, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from core.models import get_session
from core.models.base import base
from core.models.job_runs import JobRun, JobRunType

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
    runs = relationship("JobRun", cascade="all,delete", back_populates="job")

    name = Column(Text, nullable=False)
    # Alembic does not work very well with native postgres Enum type so the status column is Text
    status = Column(Text, default=JobStatus.New.value, nullable=False)
    entrypoint = Column(Text, default=config.DEFAULT_ENTRYPOINT)
    requirements = Column(Text, default=config.DEFAULT_REQUIREMENTS)

    cron = Column(Text)
    aws_cron = Column(Text)
    human_cron = Column(Text)
    schedule_is_active = Column(Boolean)

    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    def schedule_job(self):
        if self.aws_cron and self.schedule_is_active:
            logging.info(f"Scheduling job: ({self.id}, {self.aws_cron}, active: {self.schedule_is_active})")
            scheduler.schedule(self.aws_cron, str(self.id), self.schedule_is_active)

    def get_sorted_job_runs(self):
        return sorted(self.runs, key=lambda o: o.created_at, reverse=True)

    # TODO: fix notation
    def execute(self, type_: JobRunType):
        """
        Executing the job.

        Managing Job.status lifecycle, creating corresponding JobRun instance
        """
        session = get_session()

        self.status = JobStatus.Executing.value
        job_run = JobRun(job_id=self.id,
                         type=type_)
        session.add(job_run)
        session.commit()

        exit_code = job_run.execute()

        if exit_code == 0:
            self.status = JobStatus.Ok.value
        else:
            self.status = JobStatus.Failed.value

        session.commit()

    def __repr__(self):
        return '<Job %r %r %r>' % (self.id, self.name, self.aws_cron)
