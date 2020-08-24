from datetime import datetime
from typing import Optional, List

from werkzeug.datastructures import FileStorage

import config
from core.helpers import get_cron_next_execution, parse_cron
from core.models import get_session
from core.models.job_run_logs import JobRunLog
from core.models.job_runs import JobRun, JobRunStatus, JobRunType
from core.models.jobs import Job, JobStatus
from core.models.users import User, UserAccountType, ACCOUNT_LIMITS_BY_TYPE
from core.socket_signals import send_update
from job_executor import project, executor
from job_executor.exceptions import ExecutorBuildException
from job_executor.project import JobType, remove_project_from_s3, ProjectValidationError
from job_executor.scheduler import remove_job_schedule

EXECUTION_TIMELINE_HISTORY_LIMIT = 5


class JobNotFoundException(Exception):
    pass


class JobsQuotaExceededException(Exception):
    pass


def _check_user_quotas_for_job_creation(user: User):
    """
    Checks if user has a plan which permits creation of the new job.

    Returns the existing job or raising JobsQuotaExceededException exception otherwise
    """
    account_limits = ACCOUNT_LIMITS_BY_TYPE[UserAccountType(user.account_type)]
    jobs_limit = account_limits.jobs
    if len(user.jobs) >= jobs_limit:
        raise JobsQuotaExceededException('You have reached the limit of jobs for your account')


def _update_job(job, cron, entrypoint, requirements):
    job.updated_at = datetime.utcnow()

    job.entrypoint = entrypoint
    job.requirements = requirements

    if cron:
        aws_cron, human_cron = parse_cron(cron)
        job.cron = cron
        job.aws_cron = aws_cron
        job.human_cron = human_cron

        if job.schedule_is_active is None:
            job.schedule_is_active = True
    return job


def _create_job(name, cron, entrypoint, requirements, user_id):
    session = get_session()

    job_attributes = {
        'name': name,
        'user_id': user_id,
        'entrypoint': entrypoint,
        'requirements': requirements
    }
    if cron:
        aws_cron, human_cron = parse_cron(cron)
        job_attributes.update({
            "cron": cron,
            "aws_cron": aws_cron,
            "human_cron": human_cron,
            "schedule_is_active": True})

    job = Job(**job_attributes)
    session.add(job)
    return job


def delete(name: str, user: User):
    session = get_session()

    job = user.jobs.filter_by(name=name).one_or_none()
    if not job:
        raise JobNotFoundException("Job Not Found")

    job_id = job.id

    remove_job_schedule(job_id)
    remove_project_from_s3(job_id)

    session.delete(job)
    session.commit()
    return job_id


def publish(name: str, cron: str, entrypoint: str, requirements: str, user: User, project_file: FileStorage):
    session = get_session()

    existing_job = session.query(Job).filter_by(name=name, user_id=user.id).one_or_none()
    if existing_job:
        job = _update_job(existing_job, cron, entrypoint, requirements)
    else:
        _check_user_quotas_for_job_creation(user)
        job = _create_job(name, cron, entrypoint, requirements, user.id)

    session.commit()
    job.schedule_job()

    project.create(project_file, user.api_key, JobType.PUBLISHED, str(job.id))

    return job, bool(existing_job)


def get(job_id: str, user_id: str) -> Job:
    session = get_session()
    base_q = session.query(Job)

    if user_id == config.SCHEDULER_USER_ID:
        # if our automation executing script - do not check the user
        job_q = base_q.filter_by(id=job_id)
    else:
        job_q = base_q.filter_by(id=job_id, user_id=user_id)

    job = job_q.one_or_none()

    if job is None:
        raise JobNotFoundException("Job Not Found")
    return job


def execute_by_schedule(job_id: str):
    return execute(job_id, JobRunType.Schedule.value, config.SCHEDULER_USER_ID)


def execute_by_button(job_id: str, user_id: str):
    return execute(job_id, JobRunType.RunButton.value, user_id)


def execute(job_id: str, trigger_type: str, user_id: str):
    """
    Implementing the logic of Job execution
    """
    session = get_session()

    job = get(job_id, user_id)
    job.status = JobStatus.Executing.value

    exit_code = _trigger_job_run(job, trigger_type)

    if exit_code == 0:
        job.status = JobStatus.Ok.value
    else:
        job.status = JobStatus.Failed.value

    session.commit()


def get_next_executions(job_id: str, user_id: str) -> Optional[str]:
    job = get(job_id, user_id)
    if not job.schedule_is_active:
        return None
    return get_cron_next_execution(job.cron)


def get_prev_executions(job_id: str, user_id: str) -> List[JobRun]:
    job = get(job_id, user_id)
    return job.runs.limit(EXECUTION_TIMELINE_HISTORY_LIMIT)


# TODO: add return notation
def get_code(job_id: str, user_id: str):
    job = get(job_id, user_id)
    code = project.fetch_project_from_s3(job.id)
    return code


def get_logs_for_run(job_id: str, user_id: str, job_run_id: str) -> List[JobRunLog]:
    job = get(job_id, user_id)
    job_run = job.runs.get(job_run_id)
    return job_run.logs


def enable_schedule(job_id: str, user_id: str):
    job = get(job_id, user_id)
    job.schedule_is_active = False
    get_session().commit()


def disable_schedule(job_id: str, user_id: str):
    job = get(job_id, user_id)
    job.schedule_is_active = False
    get_session().commit()


def get_jobs_for_user(email: str):
    session = get_session()
    user = User.get_user_from_email(email, session)
    return user.jobs


def _trigger_job_run(job: Job, trigger_type: str) -> int:
    session = get_session()

    job_run = JobRun(job_id=job.id, type=trigger_type)
    session.add(job_run)
    session.commit()  # we need to have an id generated before we start writing logs

    path_to_job_files = project.get_path_to_job(project.JobType.PUBLISHED, job.user.api_key, job.id)

    try:
        executor_result = executor.execute(path_to_job_files, job.entrypoint, job.requirements)
    except ExecutorBuildException as exc:
        logs, exit_code = (el for el in [str(exc)]), 1
    else:
        logs, exit_code = executor_result.output, executor_result.exit_code

    for line in logs:
        _create_log_entry(line, job.id, job_run.id)

    if exit_code == 0:
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
    return exit_code


def _create_log_entry(log_msg: str, job_id: str, job_run_id: str):
    now = datetime.utcnow()
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


def execute_standalone(entrypoint: str, requirements: str, project_file: FileStorage, user: User):
    try:
        project_path = project.create(project_file, user.api_key, JobType.RUN)
        execute_result = executor.execute(project_path, entrypoint, requirements)
    except (ExecutorBuildException, ProjectValidationError) as exc:
        logs, exit_code = (el for el in [str(exc)]), 1
    else:
        logs, exit_code = execute_result.output, execute_result.exit_code
    return logs, exit_code
