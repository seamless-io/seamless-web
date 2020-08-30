import contextlib
import os
from datetime import datetime
from time import time
from typing import Optional, List, Tuple, Dict

from sqlalchemy.exc import IntegrityError
from werkzeug.datastructures import FileStorage

import config
from helpers import get_cron_next_execution, parse_cron, get_random_string
from core.models import JobParameter, db_commit
from core.models.job_parameters import PARAMETERS_LIMIT_PER_JOB
from core.models.job_run_logs import JobRunLog
from core.models.job_runs import JobRun, JobRunStatus, JobRunType
from core.models.jobs import Job, JobStatus
from core.models.users import User, UserAccountType, ACCOUNT_LIMITS_BY_TYPE
from core.socket_signals import send_update
from core.web import get_db_session
from job_executor import project, executor
from job_executor.exceptions import ExecutorBuildException
from job_executor.project import JobType, remove_project_from_s3, ProjectValidationError, restore_project_from_s3
from job_executor.scheduler import remove_job_schedule, enable_job_schedule, disable_job_schedule

CONTAINER_NAME_PREFIX = "SEAMLESS_JOB"
EXECUTION_TIMELINE_HISTORY_LIMIT = 5


class JobNotFoundException(Exception):
    pass


class JobsQuotaExceededException(Exception):
    pass


class JobsParametersLimitExceededException(Exception):
    pass


class DuplicateParameterKeyException(Exception):
    pass


class ParameterNotFoundException(Exception):
    pass


def _generate_container_name(job_id, user_id):
    return f'{CONTAINER_NAME_PREFIX}_{job_id}_USER_{user_id}_{time()}_{get_random_string(6)}'


def _check_user_quotas_for_job_creation(user: User):
    """
    Checks if user has a plan which permits creation of the new job.

    Returns the existing job or raising JobsQuotaExceededException exception otherwise
    """
    account_limits = ACCOUNT_LIMITS_BY_TYPE[UserAccountType(user.account_type)]
    jobs_limit = account_limits.jobs
    if len(list(user.jobs)) >= jobs_limit:
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
    get_db_session().add(job)
    return job


def delete(name: str, user: User):
    job = user.jobs.filter_by(name=name).one_or_none()
    if not job:
        raise JobNotFoundException("Job Not Found")

    job_id = job.id

    remove_job_schedule(job_id)
    remove_project_from_s3(job_id)

    get_db_session().delete(job)
    db_commit()
    return job_id


def publish(name: str, cron: str, entrypoint: str, requirements: str, user: User, project_file: FileStorage):
    existing_job = get_db_session().query(Job).filter_by(name=name, user_id=user.id).one_or_none()
    if existing_job:
        job = _update_job(existing_job, cron, entrypoint, requirements)
    else:
        _check_user_quotas_for_job_creation(user)
        job = _create_job(name, cron, entrypoint, requirements, user.id)

    db_commit()
    job.schedule_job()

    project.create(project_file, user.api_key, JobType.PUBLISHED, str(job.id))

    return job, bool(existing_job)


def get(job_id: str, user_id: str) -> Job:
    job = get_db_session().query(Job).filter_by(id=job_id, user_id=user_id).one_or_none()

    if job is None:
        raise JobNotFoundException("Job Not Found")
    return job


def get_user_id_from_job(job_id: str):
    job = get_db_session().query(Job).filter_by(id=job_id).one_or_none()

    if job is None:
        raise JobNotFoundException("Job Not Found")
    else:
        return job.user_id


def execute_by_schedule(job_id: str, user_id: str):
    return execute(job_id, JobRunType.Schedule.value, user_id)


def execute_by_button(job_id: str, user_id: str):
    return execute(job_id, JobRunType.RunButton.value, user_id)


def execute(job_id: str, trigger_type: str, user_id: str):
    """
    Implementing the logic of Job execution
    """
    job = get(job_id, user_id)
    job.status = JobStatus.Executing.value

    exit_code = _trigger_job_run(job, trigger_type, user_id)

    if exit_code == 0:
        job.status = JobStatus.Ok.value
    else:
        job.status = JobStatus.Failed.value

    db_commit()


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
    job_run = job.runs.filter_by(id=job_run_id).first()
    return job_run.logs


def enable_schedule(job_id: str, user_id: str):
    job = get(job_id, user_id)
    enable_job_schedule(job_id)
    job.schedule_is_active = True
    db_commit()


def disable_schedule(job_id: str, user_id: str):
    job = get(job_id, user_id)
    disable_job_schedule(job_id)
    job.schedule_is_active = False
    db_commit()


def get_jobs_for_user(email: str):
    user = User.get_user_from_email(email, get_db_session())
    return user.jobs


def get_parameters_for_job(job_id: str, user_id: str) -> List[JobParameter]:
    job = get(job_id, user_id)
    return job.parameters


def add_parameters_to_job(job_id: str, user_id: str, parameters: List[Tuple[str, str]]):
    job = get(job_id, user_id)
    if len(list(job.parameters)) + len(parameters) > PARAMETERS_LIMIT_PER_JOB:
        raise JobsParametersLimitExceededException(f"You cannot have more than {PARAMETERS_LIMIT_PER_JOB} "
                                                   f"Parameters per single Job.")
    for key, value in parameters:
        parameter = JobParameter(job_id=job.id, key=key, value=value)
        get_db_session().add(parameter)
    try:
        db_commit()
    except IntegrityError as e:
        # Potential duplicate Key value. Let's check.
        existing_keys = set([parameter.key for parameter in job.parameters])
        new_keys = set([key for key, value in parameters])
        duplicate_keys = set.intersection(existing_keys, new_keys)
        if len(duplicate_keys) > 0:
            raise DuplicateParameterKeyException("Parameter with the same Key already exists.")
        else:
            raise e


def delete_job_parameter(job_id: str, user_id: str, parameter_id: str):
    job = get(job_id, user_id)
    affected_rows = job.parameters.filter_by(id=parameter_id).delete()
    if affected_rows == 0:
        raise ParameterNotFoundException(f'Cannot delete parameter {parameter_id}: Not Found')
    db_commit()


def restore_project_if_not_exists(path_to_job_files: str, job_id: str):
    """
    Creates a folder with user's jobs in `user_projects` folder if it is not exists.
    """
    if not os.path.exists(path_to_job_files):
        restore_project_from_s3(path_to_job_files, job_id)


def _trigger_job_run(job: Job, trigger_type: str, user_id: str) -> Optional[int]:
    job_run = JobRun(job_id=job.id, type=trigger_type)
    get_db_session().add(job_run)
    db_commit()  # we need to have an id generated before we start writing logs

    send_update(
        'status',
        {
            'job_id': str(job.id),
            'job_run_id': str(job_run.id),
            'status': job_run.status
        },
        user_id
    )

    job_entrypoint = job.entrypoint or config.DEFAULT_ENTRYPOINT
    job_requirements = job.requirements or config.DEFAULT_REQUIREMENTS

    path_to_job_files = project.get_path_to_job(project.JobType.PUBLISHED, job.user.api_key, str(job.id))
    restore_project_if_not_exists(path_to_job_files, str(job.id))

    try:
        with executor.execute(path_to_job_files,
                              job_entrypoint,
                              job.get_parameters_as_dict(),
                              job_requirements,
                              _generate_container_name(str(job.id), user_id)) as executor_result:
            logs, get_exit_code = executor_result.output, executor_result.get_exit_code
            for line in logs:
                _create_log_entry(line, str(job.id), str(job_run.id), user_id)
            exit_code = get_exit_code()
    except ExecutorBuildException as exc:
        logs, get_exit_code = (el for el in [str(exc)]), lambda: 1
        for line in logs:
            _create_log_entry(line, str(job.id), str(job_run.id), user_id)
        exit_code = get_exit_code()

    if exit_code == 0:
        job_run.status = JobRunStatus.Ok.value
    else:
        job_run.status = JobRunStatus.Failed.value
    db_commit()

    send_update(
        'status',
        {
            'job_id': str(job.id),
            'job_run_id': str(job_run.id),
            'status': job_run.status
        },
        user_id
    )

    return exit_code


def _create_log_entry(log_msg: str, job_id: str, job_run_id: str, user_id: str):
    now = datetime.utcnow()
    job_run_log = JobRunLog(job_run_id=job_run_id, timestamp=now, message=log_msg)

    send_update(
        'logs',
        {
            'job_id': job_id,
            'job_run_id': job_run_id,
            'message': log_msg,
            'timestamp': str(now)
        },
        user_id
    )

    get_db_session().add(job_run_log)


@contextlib.contextmanager
def execute_standalone(entrypoint: str,
                       requirements: str,
                       project_file: FileStorage,
                       user: User):
    parameters: Dict[str, str] = {}  # TODO implement a way to pass parameters during `smls run`
    try:
        project_path = project.create(project_file, user.api_key, JobType.RUN)
        with executor.execute(project_path,
                              entrypoint,
                              parameters,
                              requirements,
                              _generate_container_name('STANDALONE', str(user.id))) as execute_result:
            logs, get_exit_code = execute_result.output, execute_result.get_exit_code
            yield (logs, get_exit_code)
    except (ExecutorBuildException, ProjectValidationError) as exc:
        logs, get_exit_code = (el for el in [str(exc)]), lambda: 1
        yield logs, get_exit_code
