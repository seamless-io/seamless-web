import logging

from flask import Blueprint, Response, jsonify, session, request, send_file
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

import config

from core import services
from core.helpers import row2dict
from core.web import requires_auth

from job_executor import project, executor

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
    jobs = services.job.get_jobs_for_user(email)
    rv = [row2dict(job) for job in jobs]
    return jsonify(rv), 200


@jobs_bp.route('/jobs/<job_id>', methods=['GET'])
@requires_auth
def get_job(job_id):
    job = services.job.get(job_id, session['profile']['internal_user_id'])
    return jsonify(row2dict(job)), 200


@jobs_bp.route('/jobs/<job_id>/schedule', methods=['PUT'])
@requires_auth
def enable_job(job_id):
    """
    If job is scheduled - enables schedule
    """
    user_id = session['profile']['internal_user_id']
    if request.args.get('is_enabled') == 'true':
        services.job.enable_schedule(job_id, user_id)
    else:
        services.job.disable_schedule(job_id, user_id)
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
    prev_executions = services.job.get_prev_executions(job_id, session['profile']['internal_user_id'])
    return jsonify({'last_executions': [{'status': run.status,
                                         'created_at': run.created_at,
                                         'run_id': run.id} for run in prev_executions]}), 200


@jobs_bp.route('/publish', methods=['PUT'])
def create_job():
    api_key = request.headers.get('Authorization')
    if not api_key:
        return Response('Not authorized request', 401)

    try:
        user = services.user.get(api_key)
    except services.user.UserNotFoundException as e:
        return Response(str(e), 400)

    project_file = request.files.get('seamless_project')
    if not project_file:
        return Response('File not provided', 400)

    job_name = request.args.get('name')
    cron_schedule = request.args.get('schedule')
    entrypoint = request.args.get('entrypoint')
    requirements = request.args.get('requirements')

    logging.info(
        f"Received 'publish': job_name={job_name}, schedule={cron_schedule}, "
        f"entrypoint={entrypoint}, requirements={requirements}"
    )

    try:
        job, is_existing = services.job.publish(
            job_name,
            cron_schedule,
            entrypoint,
            requirements,
            user,
            project_file
        )
    except services.job.JobsQuotaExceededException as e:
        return Response(str(e), 400)  # TODO: ensure that error code is correct
    except project.ProjectValidationError as e:
        return Response(str(e), 400)  # TODO: ensure that error code is correct

    return jsonify({'job_id': job.id,
                    'existing_job': is_existing}), 200


@jobs_bp.route('/jobs/execute', methods=['POST'])
@auth.login_required
def run_job_by_schedule():
    """
    Executing job which was scheduled
    """
    job_id = request.json['job_id']
    logging.info(f"Running job {job_id} based on schedule")
    services.job.execute_by_schedule(job_id)
    return f"Running job {job_id}", 200


@jobs_bp.route('/jobs/<job_id>/run', methods=['POST'])
@requires_auth
def run_job(job_id):
    """
    Executing job when triggered manually via UI
    """
    services.job.execute_by_button(job_id, session['profile']['internal_user_id'])
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

    try:
        user = services.user.get(api_key)
    except services.user.UserNotFoundException as e:
        return Response(str(e), 400)

    job_id = services.job.delete(job_name, user)

    logging.info(f"Deleted job {job_id} from the database")
    return f"Successfully deleted job {job_id}", 200


@jobs_bp.route('/jobs/<job_id>/next_execution', methods=['GET'])
@requires_auth
def get_next_job_execution(job_id):
    next_execution = services.job.get_next_executions(job_id, session['profile']['internal_user_id'])
    if not next_execution:
        rv = "Not scheduled"
    else:
        rv = next_execution
    return jsonify({"result": rv}), 200


@jobs_bp.errorhandler(services.job.JobNotFoundException)
def handle_error(e):
    return jsonify(error=str(e)), 404
