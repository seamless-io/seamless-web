import datetime
from typing import Optional, List, Dict

import config

from core.models import get_session
from core.helpers import get_cron_next_execution
from core.socket_signals import send_update
from core.models.jobs import Job, JobStatus
from core.models.job_runs import JobRun, JobRunStatus
from core.models.job_run_logs import JobRunLog

# from job_executor.project import JobType, fetch_project_from_s3, remove_project_from_s3

from job_executor import project, executor


EXECUTION_TIMELINE_HISTORY_LIMIT = 5


class JobNotFoundException(Exception):
    pass


def create():
    pass



def _get_job(job_id: str, user_id: str) -> Job:
    session = get_session()
    base_q = session.query(Job)

    if user_id == config.SCHEDULER_USER_ID:
        # if our automation executing script - do not check the user
        job_q = base_q.filter_by(id=job_id)
    else:
        job_q = base_q.query(Job).filter_by(id=job_id, user_id=user_id)

    job = job_q.one_or_none()

    if job is None:
        raise JobNotFoundException("Job Not Found")
    return job


def execute(job_id: str, trigger_type: str, user_id: str):
    """
    Implementing the logic of Job execution
    """
    session = get_session()

    job = _get_job(job_id, user_id)
    job.status = JobStatus.Executing.value

    exit_code = _trigger_job_run(job, trigger_type)

    if exit_code == 0:
        job.status = JobStatus.Ok.value
    else:
        job.status = JobStatus.Failed.value

    session.commit()


def get_next_executions(job_id: str, user_id: str) -> Optional[List]:
    session = get_session()

    job = db_session.query(Job).get(job_id)

    if not job.schedule_is_active:
        return None

    return get_cron_next_execution(job.cron)


def get_prev_executions(job_id: str, user_id: str) -> List[JobRun]:
    job = _get_job(job_id, user_id)
    return job.runs.limit(EXECUTION_TIMELINE_HISTORY_LIMIT)


# TODO: add return notation
def get_code(job_id: str, user_id: str):
    job = _get_job(job_id, user_id)
    code = project.fetch_project_from_s3(job.id)
    return code


def get_logs_for_run(job_id: str, user_id: str, job_run_id: str) -> List[JobRunLog]:
    job = _get_job(job_id, user_id)
    job_run = job.runs.get(job_run_id)
    return job_run.logs


def enable_schedule(job_id: str, user_id: str):
    job = _get_job(job_id, user_id)
    job.schedule_is_active = False
    get_session().commit()


def disable_schedule(job_id: str, user_id: str):
    job = _get_job(job_id, user_id)
    job.schedule_is_active = False
    get_session().commit()


def _trigger_job_run(job: Job, trigger_type: str) -> int:
    session = get_session()

    job_run = JobRun(job_id=job.id, type=trigger_type)
    session.add(job_run)
    session.commit()  # we need to have an id generated before we start writing logs

    path_to_job_files = project.get_path_to_job(project.JobType.PUBLISHED, job.user.api_key, job.id)
    executor_result = executor.execute(path_to_job_files, job.entrypoint, job.requirements)

    for line in executor_result.output:
        now = datetime.datetime.utcnow()
        _create_log_entry(line, job.id, job_run.id)

    if executor_result.exit_code == 0:
        job_run.status = JobRunStatus.Ok.value
    else:
        job_run.status = JobRunStatus.Failed.value

    send_update(
        'status',
        {
            'job_id': job.id,
            'job_run_id': job_run.id,
            'status': job_run.status
        },
    )

    session.commit()
    return executor_result.exit_code


def _create_log_entry(log_msg: str, job_id: str, job_run_id: str):
    now = datetime.datetime.utcnow()
    session = get_session()
    job_run_log = JobRunLog(job_run_id=job_run_id, timestamp=now, message=log_msg)

    send_update(
        'logs',
        {
            'job_id': job_id,
            'job_run_id': job_run_id,
            'message': log_msg,
            'timestamp': str(now)
        }
    )

    session.add(job_run_log)
