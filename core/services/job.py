import io
from datetime import datetime
from time import time
from typing import Optional, List, Tuple

from sqlalchemy.exc import IntegrityError

import constants
import core.storage as storage
from core.models import JobParameter, db_commit
from core.models.job_parameters import PARAMETERS_LIMIT_PER_JOB
from core.models.job_run_logs import JobRunLog
from core.models.job_runs import JobRun, JobRunStatus, JobRunType
from core.models.jobs import Job, JobStatus
from core.models.users import User, UserAccountType, ACCOUNT_LIMITS_BY_TYPE
from core.services import workspace as workspace_service
from core.socket_signals import send_update
from core.web import get_db_session
from helpers import get_cron_next_execution, parse_cron, get_random_string
from job_executor import executor
from job_executor.exceptions import ExecutorBuildException
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


def _create_job_in_db(name, cron, entrypoint, requirements, user_id, schedule_is_active, workspace_id):
    job_attributes = {
        'name': name,
        'user_id': user_id,
        'entrypoint': entrypoint,
        'requirements': requirements,
        'workspace_id': workspace_id
    }
    if cron:
        aws_cron, human_cron = parse_cron(cron)
        job_attributes.update({
            "cron": cron,
            "aws_cron": aws_cron,
            "human_cron": human_cron,
            "schedule_is_active": schedule_is_active})

    job = Job(**job_attributes)
    get_db_session().add(job)
    return job


def get_job_by_name(name: str, user_id: int, workspace_id: Optional[int] = None):
    if not workspace_id:
        workspace_id = workspace_service.get_default_workspace(user_id).id
    job = get_db_session().query(Job).filter_by(name=name, user_id=user_id, workspace_id=workspace_id).one_or_none()
    if not job:
        raise JobNotFoundException("Job Not Found")
    return job


def delete(job_id: int, user_id: int, workspace_id: Optional[int] = None):
    job = get(job_id, user_id, workspace_id)

    remove_job_schedule(job_id)
    storage.delete(storage.Type.Job, job_id)

    get_db_session().delete(job)
    db_commit()
    return job_id


def publish(name: str, cron: str, entrypoint: str, requirements: str, user: User, project_file: io.BytesIO,
            workspace_id: str, schedule_is_active=True):
    existing_job = get_db_session().query(Job).filter_by(name=name, user_id=user.id).one_or_none()
    if existing_job:
        job = _update_job(existing_job, cron, entrypoint, requirements)
    else:
        _check_user_quotas_for_job_creation(user)
        job = _create_job_in_db(name, cron, entrypoint, requirements, user.id, schedule_is_active, workspace_id)

    db_commit()
    job.schedule_job()

    storage.save(project_file, storage.Type.Job, job.id)

    return job, bool(existing_job)


def get(job_id: int, user_id: int, workspace_id: Optional[int] = None) -> Job:
    if not workspace_id:
        workspace_id = workspace_service.get_default_workspace(user_id).id
    job = get_db_session().query(Job).filter_by(id=job_id, user_id=user_id, workspace_id=workspace_id).one_or_none()

    if job is None:
        raise JobNotFoundException("Job Not Found")
    return job


def get_user_id_from_job(job_id: int):
    job = get_db_session().query(Job).filter_by(id=job_id).one_or_none()

    if job is None:
        raise JobNotFoundException("Job Not Found")
    else:
        return job.user_id


def execute_by_schedule(job_id: int, user_id: int):
    return execute(job_id, JobRunType.Schedule.value, user_id)


def execute_by_button(job_id: int, user_id: int):
    return execute(job_id, JobRunType.RunButton.value, user_id)


def execute(job_id: int, trigger_type: str, user_id: int, workspace_id: Optional[int] = None):
    """
    Implementing the logic of Job execution
    """
    job = get(job_id, user_id, workspace_id)
    job.status = JobStatus.Executing.value

    exit_code = _trigger_job_run(job, trigger_type, user_id)

    if exit_code == 0:
        job.status = JobStatus.Ok.value
    else:
        job.status = JobStatus.Failed.value

    db_commit()


def get_next_executions(job_id: int, user_id: int) -> Optional[str]:
    job = get(job_id, user_id)
    if not job.schedule_is_active:
        return None
    return get_cron_next_execution(job.cron)


def get_prev_executions(job_id: int, user_id: int) -> List[JobRun]:
    job = get(job_id, user_id)
    return job.runs.limit(EXECUTION_TIMELINE_HISTORY_LIMIT)


# TODO: add return notation
def get_code(job_id: int, user_id: int):
    get(job_id, user_id)  # Basically checking access rights for this user to this job
    code = storage.get_archive(storage.Type.Job, job_id)
    return code


def get_logs_for_run(job_id: int, user_id: int, job_run_id: int) -> List[JobRunLog]:
    job = get(job_id, user_id)
    job_run = job.runs.filter_by(id=job_run_id).first()
    return job_run.logs


def update_schedule(job_id: int, user_id: int, cron: str):
    job = get(job_id, user_id)

    aws_cron, human_cron = parse_cron(cron)
    job.cron = cron
    job.aws_cron = aws_cron
    job.human_cron = human_cron
    db_commit()

    job.schedule_job()


def enable_schedule(job_id: int, user_id: int):
    job = get(job_id, user_id)
    enable_job_schedule(job_id)
    job.schedule_is_active = True
    db_commit()


def disable_schedule(job_id: int, user_id: int):
    job = get(job_id, user_id)
    disable_job_schedule(job_id)
    job.schedule_is_active = False
    db_commit()


def get_parameters_for_job(job_id: int, user_id: int) -> List[JobParameter]:
    job = get(job_id, user_id)
    return job.parameters


def add_parameters_to_job(job_id: int, user_id: int, parameters: List[Tuple[str, Optional[str]]]):
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


def update_job_parameter(job_id: int, user_id: int, parameter_id: int, param_key: str, param_value: str):
    job = get(job_id, user_id)
    found_parameter = job.parameters.filter_by(id=parameter_id).one_or_none()
    if not found_parameter:
        raise ParameterNotFoundException(f'Cannot update parameter {parameter_id}: Not Found')
    found_parameter.key = param_key
    found_parameter.value = param_value
    db_commit()


def delete_job_parameter(job_id: int, user_id: int, parameter_id: int):
    job = get(job_id, user_id)
    affected_rows = job.parameters.filter_by(id=parameter_id).delete()
    if affected_rows == 0:
        raise ParameterNotFoundException(f'Cannot delete parameter {parameter_id}: Not Found')
    db_commit()


def link_job_to_template(job: Job, template_id: int):
    job.job_template_id = template_id
    db_commit()


def make_job_name_unique(job_name: str, user_id: int):
    """
    If we can't find existing Job with the name provided - just return it, its unique.
    If we can - add suffix to the name to make it unique.
    "<Original Name> 2", if exists, "<Original Name> 3", etc
    """
    try:
        name_suffix = ''
        # Any big enough number is fine, just not too big, so we don't load our system accidentally
        for i in range(2, 50):
            result_name = job_name + name_suffix
            get_job_by_name(result_name, user_id)
            name_suffix = str(i)
    except JobNotFoundException:
        return result_name  # This is fine, that means there is no Job with the template name we're adding
    raise Exception("Impossible Error: we have 49 Jobs with the same 'base' name. Something is fucked up bad.")


def _trigger_job_run(job: Job, trigger_type: str, user_id: int) -> Optional[int]:
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

    job_entrypoint = job.entrypoint or constants.DEFAULT_ENTRYPOINT
    job_requirements = job.requirements or constants.DEFAULT_REQUIREMENTS

    path_to_job_files = storage.get_path_to_files(storage.Type.Job, job.id)

    try:
        with executor.execute(path_to_job_files,
                              job_entrypoint,
                              job.get_parameters_as_dict(),
                              job_requirements,
                              _generate_container_name(str(job.id), user_id)) as executor_result:
            logs, get_exit_code = executor_result.output, executor_result.get_exit_code
            for line in logs:
                _create_log_entry(line, job.id, job_run.id, user_id)
            exit_code = get_exit_code()
    except ExecutorBuildException as exc:
        logs, get_exit_code = (el for el in [str(exc)]), lambda: 1
        for line in logs:
            _create_log_entry(line, job.id, job_run.id, user_id)
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


def _create_log_entry(log_msg: str, job_id: int, job_run_id: int, user_id: int):
    now = datetime.utcnow()
    job_run_log = JobRunLog(job_run_id=job_run_id, timestamp=now, message=log_msg)

    send_update(
        'logs',
        {
            'job_id': str(job_id),
            'job_run_id': str(job_run_id),
            'message': log_msg,
            'timestamp': str(now)
        },
        user_id
    )

    get_db_session().add(job_run_log)
