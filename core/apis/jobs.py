import logging
from datetime import datetime

from flask import Blueprint, Response, jsonify, session, request, send_file
from flask_httpauth import HTTPBasicAuth
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.security import check_password_hash, generate_password_hash

from core import services
from core.models import session_scope
from core.helpers import row2dict, parse_cron, get_cron_next_execution
from core.models.job import Job
from core.models.users import User
from core.models.job_runs import JobRunType, JobRun
from core.models.userss import UserAccountType, ACCOUNT_LIMITS_BY_TYPE
from core.web import requires_auth
import config
from job_executor import project, executor
from job_executor.scheduler import enable_job_schedule, disable_job_schedule, remove_job_schedule

jobs_bp = Blueprint('jobs', __name__)

TIMESTAMP_FOR_LOGS_FORMAT = "%m_%d_%Y_%H_%M_%S_%f"

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    """
    We are going to authenticate scheduler using hardcoded password
    """
    if username == 'schedule' and check_password_hash(
            generate_password_hash(config.LAMBDA_PROXY_PASSWORD), password):
        return username


@jobs_bp.route('/jobs', methods=['GET'])
@requires_auth
def get_jobs():
    email = session['profile']['email']
    with session_scope() as db_session:
        user = User.get_user_from_email(email, db_session)
        jobs = [row2dict(job) for job in user.jobs]

        return jsonify(jobs), 200


@jobs_bp.route('/jobs/<job_id>', methods=['GET'])
@requires_auth
def get_job(job_id):
    with session_scope() as db_session:
        job = db_session.query(Job).get(job_id)
        if not job or job.user_id != session['profile']['internal_user_id']:
            return "Job Not Found", 404
        return jsonify(row2dict(job)), 200


@jobs_bp.route('/jobs/<job_id>', methods=['PUT'])
@requires_auth
def update_job(job_id):
    allowed_fields = ['schedule_is_active']
    data = request.json
    with session_scope() as db_session:
        job = db_session.query(Job).get(job_id)
        if not job or job.user_id != session['profile']['internal_user_id']:
            return "Job Not Found", 404
        for key, value in data.items():
            if key not in allowed_fields:
                return f"{key} field is not allowed to be updated", 400
            setattr(job, key, value)
            if key == 'schedule_is_active':
                if value:
                    enable_job_schedule(job_id)
                else:
                    disable_job_schedule(job_id)
        db_session.commit()
        return jsonify(row2dict(job)), 200


@jobs_bp.route('/jobs/<job_id>/schedule', methods=['PUT'])
@requires_auth
def enable_job(job_id):
    """
    If job is scheduled - enables schedule
    """
    user_id = session['profile']['internal_user_id']
    if request.args.get('is_enabled') == 'true':
        service.job.enable_schedule(job_id, user_id)
    else:
        service.job.disable_schedule(job_id, user_id)
    return jsonify(job_id), 200


@jobs_bp.route('/jobs/<job_id>/runs/<job_run_id>/logs', methods=['GET'])
@requires_auth
def get_job_logs(job_id: str, job_run_id: str):
    job_run_logs = services.job.get_logs_for_run(job_id, session['profile']['internal_user_id'], job_run_id)
    logs = [row2dict(log_record) for log_record in job_run_logs]
    return jsonify(logs), 200


@jobs_bp.route('/jobs/<job_id>/code', methods=['GET'])
@requires_auth
def get_job_code(job_id: str):
    code = services.job.get_code(job_id, session['profile']['internal_user_id'])
    return send_file(code, attachment_filename=f'job_{job_id}.tar.gz'), 200


@jobs_bp.route('/jobs/<job_id>/executions', methods=['GET'])
@requires_auth
def get_job_executions_history(job_id: str):
    with session_scope() as db_session:
        prev_executions = services.job.get_prev_executions(job_id, session['profile']['internal_user_id'])
        return jsonify({'last_executions': [{'status': run.status,
                                             'created_at': run.created_at,
                                             'run_id': run.id} for run in prev_executions]}), 200


@jobs_bp.route('/publish', methods=['PUT'])
def create_job():
    api_key = request.headers.get('Authorization')
    if not api_key:
        return Response('Not authorized request', 401)

    file = request.files.get('seamless_project')
    if not file:
        return Response('File not provided', 400)

    job_name = request.args.get('name')
    cron_schedule = request.args.get('schedule')
    entrypoint = request.args.get('entrypoint')
    requirements = request.args.get('requirements')

    logging.info(
        f"Received 'publish': job_name={job_name}, schedule={cron_schedule}, "
        f"entrypoint={entrypoint}, requirements={requirements}"
    )

    with session_scope() as session:
        try:
            user = User.get_user_from_api_key(api_key, session)
        except NoResultFound:
            return Response('API Key is wrong, please go to our account https://app.seamlesscloud.io/account,'
                            ' copy the API Key field and run "smls init <api key>"', 400)

        account_limits = ACCOUNT_LIMITS_BY_TYPE[UserAccountType(user.account_type)]
        jobs_limit = account_limits.jobs
        jobs = list(user.jobs)

        job = None
        for j in jobs:
            if j.name == job_name:
                job = j
                break
        if job:  # The user re-publishes an existing job
            existing_job = True
            job.updated_at = datetime.utcnow()
            if cron_schedule:
                aws_cron, human_cron = parse_cron(cron_schedule)
                job.cron = cron_schedule
                job.aws_cron = aws_cron
                job.human_cron = human_cron

                job.entrypoint = entrypoint
                job.requirements = requirements

                if job.schedule_is_active is None:
                    job.schedule_is_active = True
        else:  # The user publishes the new job
            if len(jobs) >= jobs_limit:
                return Response('You have reached the limit of jobs for your account', 400)
            existing_job = False
            job_attributes = {
                'name': job_name,
                'user_id': user.id,
                'entrypoint': entrypoint,
                'requirements': requirements
            }
            if cron_schedule:
                aws_cron, human_cron = parse_cron(cron_schedule)
                job_attributes.update({
                    "cron": cron_schedule,
                    "aws_cron": aws_cron,
                    "human_cron": human_cron,
                    "schedule_is_active": True})
            job = Job(**job_attributes)
            session.add(job)

        session.commit()
        job.schedule_job()
        job_id = job.id

    try:
        project.create(file, api_key, JobType.PUBLISHED, str(job_id))
    except project.ProjectValidationError as exc:
        return Response(str(exc), 400)

    return jsonify({'job_id': job_id,
                    'existing_job': existing_job}), 200


@jobs_bp.route('/jobs/execute', methods=['POST'])
@auth.login_required
def run_job_by_schedule():
    """
    Executing job which was scheduled
    """
    logging.info(f"Running job {job_id} based on schedule")
    services.job.execute(request.json['job_id'], JobRunType.Schedule.value, config.SCHEDULER_USER_ID)
    return f"Running job {job_id}", 200


@jobs_bp.route('/jobs/<job_id>/run', methods=['POST'])
@requires_auth
def run_job(job_id):
    """
    Executing job when triggered manually via UI
    """
    services.job.execute(job_id, JobRunType.RunButton.value, session['profile']['internal_user_id'])
    return f"Running job {job_id}", 200


@jobs_bp.route('/run', methods=['POST'])
def run() -> Response:
    """
    Exeucting job when triggered manually via CLI
    """
    api_key = request.headers.get('Authorization')
    if not api_key:
        return Response('Not authorized request', 401)

    file = request.files.get('seamless_project')

    entrypoint = str(request.args.get('entrypoint', 'function.main'))
    requirements = str(request.args.get('requirements', 'requirements.txt'))

    if not file:
        return Response('File not provided', 400)

    try:
        project_path = project.create(file, api_key, JobType.RUN)
    except project.ProjectValidationError as exc:
        return Response(str(exc), 400)

    executor_result = executor.execute(project_path, entrypoint, requirements)

    # TODO: return exit code
    return Response(list(executor_result.output), content_type="text/event-stream", headers={'X-Accel-Buffering': 'no'})


@jobs_bp.route('/jobs/<job_name>', methods=['DELETE'])
def delete_job(job_name):
    api_key = request.headers.get('Authorization')
    if not api_key:
        return Response('Not authorized request', 401)

    with session_scope() as db_session:
        user = User.get_user_from_api_key(api_key, db_session)
        job = None
        for j in user.jobs:
            if j.name == job_name:
                job = j
                break

        if not job:
            return "Job Not Found", 404

        job_id = job.id

        remove_job_schedule(job_id)
        remove_project_from_s3(job_id)

        db_session.delete(job)
        db_session.commit()
        logging.info(f"Deleted job {job_id} from the database")
        return f"Successfully deleted job {job_id}", 200


def _ensure_valid_job_for_user(job_id, user_id):
    with session_scope() as db_session:
        job = db_session.query(Job).get(job_id)
        if not job or job.user_id != user_id:
            return False
    return True

@jobs_bp.route('/jobs/<job_id>/next_execution', methods=['GET'])
@requires_auth
def get_next_job_execution(job_id):
    is_valid, rv, code = _ensure_valid_job_for_user(job_id, session['profile']['internal_user_id'])
    if is_valid is False:
        return "Job Not Found", 404

    next_execution = services.job.get_next_executions(job_id)
    if not next_execution:
        rv = "Not scheduled"
    else:
        rv = next_execution
    return jsonify({"result": rv}), 200


@jobs_bp.errorhandler(services.job.JobNotFoundException)
def handle_error(e):
    return jsonify(error=str(e)), 404
