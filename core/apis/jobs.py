import logging
from threading import Thread

from flask import Blueprint, Response, jsonify, session, request, send_file, current_app
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

import config
import core.services.job as job_service
import core.services.user as user_service
import helpers
from core.web import requires_auth
from helpers import row2dict
from job_executor import project
from job_executor.project import generate_project_structure, get_file_content, read_bytes_from_sent_file

jobs_bp = Blueprint('jobs', __name__)

TIMESTAMP_FOR_LOGS_FORMAT = "%m_%d_%Y_%H_%M_%S_%f"

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    """
    We are going to authenticate scheduler using hardcoded password
    """
    if username == config.LAMBDA_PROXY_AUTH_USERNAME and check_password_hash(
            generate_password_hash(config.LAMBDA_PROXY_PASSWORD), password):
        return username


@jobs_bp.route('/jobs', methods=['GET'])
@requires_auth
def get_jobs():
    email = session['profile']['email']
    jobs = job_service.get_jobs_for_user(email)
    rv = [row2dict(job) for job in jobs]
    return jsonify(rv), 200


@jobs_bp.route('/jobs/<job_id>', methods=['GET'])
@requires_auth
def get_job(job_id):
    job = job_service.get(job_id, session['profile']['internal_user_id'])
    return jsonify(row2dict(job)), 200


@jobs_bp.route('/jobs/<job_id>/schedule', methods=['PUT'])
@requires_auth
def enable_job(job_id):
    """
    If job is scheduled - enables schedule
    """
    user_id = session['profile']['internal_user_id']
    if request.args.get('is_enabled') == 'true':
        job_service.enable_schedule(job_id, user_id)
    else:
        job_service.disable_schedule(job_id, user_id)
    return jsonify(job_id), 200


@jobs_bp.route('/jobs/<job_id>/runs/<job_run_id>/logs', methods=['GET'])
@requires_auth
def get_job_logs(job_id: str, job_run_id: str):
    job_run_logs = job_service.get_logs_for_run(job_id, session['profile']['internal_user_id'], job_run_id)
    logs = [row2dict(log_record) for log_record in job_run_logs]
    return jsonify(logs), 200


@jobs_bp.route('/jobs/<job_id>/code', methods=['GET'])
@requires_auth
def get_job_code(job_id: str):
    code = job_service.get_code(job_id, session['profile']['internal_user_id'])
    return send_file(code, attachment_filename=f'job_{job_id}.tar.gz'), 200


@jobs_bp.route('/jobs/<job_id>/executions', methods=['GET'])
@requires_auth
def get_job_executions_history(job_id: str):
    prev_executions = job_service.get_prev_executions(job_id, session['profile']['internal_user_id'])
    return jsonify({'last_executions': [{'status': run.status,
                                         'created_at': run.created_at,
                                         'run_id': run.id} for run in prev_executions]}), 200


@jobs_bp.route('/publish', methods=['PUT'])
def create_job():
    api_key = request.headers.get('Authorization')
    if not api_key:
        return Response('Not authorized request', 401)

    try:
        user = user_service.get_by_api_key(api_key)
    except user_service.UserNotFoundException as e:
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
        file = read_bytes_from_sent_file(project_file)
        job, is_existing = job_service.publish(
            job_name,
            cron_schedule,
            entrypoint,
            requirements,
            user,
            file
        )
    except job_service.JobsQuotaExceededException as e:
        return Response(str(e), 400)  # TODO: ensure that error code is correct
    except project.ProjectValidationError as e:
        return Response(str(e), 400)  # TODO: ensure that error code is correct
    except helpers.InvalidCronException as e:
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

    # Since this is not triggered by the user from website or CLI, we don't have the user_id in the session.
    # Thus we need to get it from the job directly.
    user_id = job_service.get_user_id_from_job(job_id)

    def background_task(app):
        # Without Flask app context we cannot use the socket connection
        with app.app_context():
            job_service.execute_by_schedule(job_id, user_id)

    thread = Thread(target=background_task, args=[current_app._get_current_object()])
    thread.start()

    return f"Running job {job_id}", 202


@jobs_bp.route('/jobs/<job_id>/run', methods=['POST'])
@requires_auth
def run_job(job_id):
    """
    Executing job when triggered manually via UI
    """
    job_service.execute_by_button(job_id, session['profile']['internal_user_id'])
    return f"Running job {job_id}", 200


@jobs_bp.route('/run', methods=['POST'])
def run() -> Response:
    """
    Executing job when triggered manually via CLI
    """
    # TODO: create a model for storing standalone executions
    api_key = request.headers.get('Authorization')
    if not api_key:
        return Response('Not authorized request', 401)

    try:
        user = user_service.get_by_api_key(api_key)
    except user_service.UserNotFoundException as exc:
        return Response(str(exc), 400)

    file = request.files.get('seamless_project')

    entrypoint = str(request.args.get('entrypoint', config.DEFAULT_ENTRYPOINT))
    requirements = str(request.args.get('requirements', config.DEFAULT_REQUIREMENTS))

    if not file:
        return Response('File not provided', 400)

    with job_service.execute_standalone(entrypoint, requirements, file, user) as (logs, _):
        return Response(logs, content_type="text/event-stream", headers={'X-Accel-Buffering': 'no'})


@jobs_bp.route('/jobs/<job_name>', methods=['DELETE'])
def delete_job(job_name):
    api_key = request.headers.get('Authorization')
    if not api_key:
        return Response('Not authorized request', 401)

    try:
        user = user_service.get_by_api_key(api_key)
    except user_service.UserNotFoundException as e:
        return Response(str(e), 400)

    job_id = job_service.delete(job_name, user)

    logging.info(f"Deleted job {job_id} from the database")
    return f"Successfully deleted job {job_id}", 200


@jobs_bp.route('/jobs/<job_id>/next_execution', methods=['GET'])
@requires_auth
def get_next_job_execution(job_id):
    next_execution = job_service.get_next_executions(job_id, session['profile']['internal_user_id'])
    if not next_execution:
        rv = "Not scheduled"
    else:
        rv = next_execution
    return jsonify({"result": rv}), 200


@jobs_bp.route('/jobs/<job_id>/parameters', methods=['GET'])
@requires_auth
def get_job_parameters(job_id: str):
    parameters = job_service.get_parameters_for_job(job_id, session['profile']['internal_user_id'])
    parameters = [row2dict(parameter) for parameter in parameters]
    return jsonify(parameters), 200


@jobs_bp.route('/jobs/<job_id>/parameters', methods=['POST'])
@requires_auth
def add_job_parameter(job_id: str):
    data = request.json
    key = data.get('key')
    value = data.get('value')
    if not (key and value):
        return Response('The payload is not valid, it needs to have both name and value', 400)
    try:
        job_service.add_parameters_to_job(job_id, session['profile']['internal_user_id'], [(key, value)])
    except job_service.JobsParametersLimitExceededException as e:
        return Response(str(e), 400)
    except job_service.DuplicateParameterKeyException as e:
        return Response(str(e), 400)
    return 'Successfully added a new parameter', 200


@jobs_bp.route('/jobs/<job_id>/parameters/<parameter_id>', methods=['DELETE'])
@requires_auth
def delete_job_parameter(job_id: str, parameter_id: str):
    try:
        job_service.delete_job_parameter(job_id, session['profile']['internal_user_id'], parameter_id)
    except job_service.ParameterNotFoundException as e:
        return Response(str(e), 404)
    return f'Successfully delete parameter {parameter_id}', 200


@jobs_bp.errorhandler(job_service.JobNotFoundException)
def handle_error(e):
    return jsonify(error=str(e)), 404


@jobs_bp.route('/jobs/<job_id>/folder', methods=['GET'])
@requires_auth
def get_project_structure(job_id: str):
    job = job_service.get(job_id, session['profile']['internal_user_id'])
    api_key = job.user.api_key
    project_structure = generate_project_structure(job_id, api_key)
    return jsonify(project_structure), 200


@jobs_bp.route('/jobs/<job_id>/file', methods=['GET'])
@requires_auth
def get_job_file(job_id: str):
    file_path = str(request.args.get('file_path'))

    job = job_service.get(job_id, session['profile']['internal_user_id'])
    api_key = job.user.api_key

    file_content = get_file_content(job_id, api_key, file_path)
    return jsonify(file_content), 200
