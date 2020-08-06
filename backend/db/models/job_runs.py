import datetime
import enum

from sqlalchemy import event
from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from backend.socket_signals import send_update
from backend.db import get_session
from backend.db.models.base import base
from job_executor import executor, project


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
    logs = relationship("JobRunLog", cascade="all,delete", back_populates="job_run")

    type = Column(Text, nullable=False)
    status = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    def __repr__(self):
        return '<JobRun %r %r %r>' % (self.id, self.type, self.status)

    def execute(self) -> int:
        session = get_session()

        self.status = JobRunStatus.Executing.value

        path_to_job_files = project.get_path_to_job(JobType.PUBLISHED, job.user.api_key, str(job.id))
        executor_result = executor.execute(path_to_job_files, entrypoint, requirements)

        for line in executor_result.output:
            now = datetime.utcnow()
            job_run_log = JobRunLog(job_run_id=str(job_run.id), timestamp=now, message=line)
            session.add(job_run_log)

        if executor_result.exit_code == 0:
            self.status = JobRunStatus.Ok.value
        else:
            self.status = JobRunStatus.Failed.value

        return executor_result.exit_code



@event.listens_for(JobRun.status, 'set')
def send_status_update_signal(target, value, oldvalue, initiator):
    send_update(
        'status',
        {
            'job_id': job.id,
            'job_run_id': job_run.id,
            'status': job.status
        },
    )
