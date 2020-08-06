import datetime

from core.models import get_session

from core.socket_signals import send_update
from core.models.jobs import Job, JobStatus
from core.models.job_runs import JobRun, JobRunStatus
from core.models.job_run_logs import JobRunLog

from job_executor import project, executor


def create():
    pass


def update():
    pass


def execute(job_id: str, trigger_type: str):
    """
    Implementing the logic of Job execution
    """
    session = get_session()

    job = session.query(Job).get(job_id)
    job.status = JobStatus.Executing.value

    exit_code = _trigger_job_run(job, trigger_type)

    if exit_code == 0:
        job.status = JobStatus.Ok.value
    else:
        job.status = JobStatus.Failed.value

    session.commit()


def _trigger_job_run(job: Job, trigger_type: str):
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
