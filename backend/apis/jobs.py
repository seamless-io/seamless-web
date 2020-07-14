import logging

from flask import Blueprint, Response, jsonify, session, request
from flask_socketio import emit
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

from backend.db import session_scope
from backend.db.helpers import row2dict
from backend.db.models import Job, User, JobRun
from backend.db.models.job_runs import JobRunType
from backend.db.models.jobs import JobStatus
from backend.web import requires_auth
from backend.config import SCHEDULE_PASSWORD
from job_executor import project, executor
from job_executor.project import get_path_to_job, JobType
from job_executor.scheduler import enable_job_schedule, disable_job_schedule


jobs_bp = Blueprint('jobs', __name__)

TIMESTAMP_FOR_LOGS_FORMAT = "%m_%d_%Y_%H_%M_%S_%f"

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    """
    We are going to authenticate scheduler using hardcoded password
    """
    if username == 'schedule' and check_password_hash(generate_password_hash(SCHEDULE_PASSWORD), password):
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


@jobs_bp.route('/jobs/<job_id>/runs', methods=['GET'])
@requires_auth
def get_job_runs(job_id: str):
    with session_scope() as db_session:
        job = db_session.query(Job).get(job_id)
        if not job or job.user_id != session['profile']['internal_user_id']:
            return "Job Not Found", 404
        job_runs = job.get_sorted_job_runs()

        return jsonify([row2dict(job_run) for job_run in job_runs]), 200


@jobs_bp.route('/jobs/<job_id>/runs/<job_run_id>/logs', methods=['GET'])
@requires_auth
def get_job_logs(job_id: str, job_run_id: str):
    with session_scope() as db_session:
        job = db_session.query(Job).get(job_id)
        if not job or job.user_id != session['profile']['internal_user_id']:
            return "Job Not Found", 404
        job_run = db_session.query(JobRun).get(job_run_id)
        logs = [row2dict(log_record) for log_record in job_run.logs]

        return jsonify(logs), 200


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

    logging.info(f"Received 'publish': job_name={job_name}, schedule={cron_schedule}")

    with session_scope() as session:
        user = User.get_user_from_api_key(api_key, session)
        job = None
        for j in user.jobs:
            if j.name == job_name:
                job = j
                break
        if job:  # The user re-publishes an existing job
            if cron_schedule:
                job.schedule = cron_schedule
                if job.schedule_is_active is None:
                    job.schedule_is_active = True
        else:  # The user publishes the new job
            job_attributes = {
                'name': job_name,
                'user_id': user.id
            }
            if cron_schedule:
                job_attributes.update({"schedule": cron_schedule,
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
                    'existing_job': job is not None}), 200


def _run_job(job_id, type_, user_id=None):
    """
    Function to execute job

    :param job_id: job ID to execute
    :param type_: execution type
    :param user_id: if passed - check if job's author is this user ID
    """
    with session_scope() as db_session:
        job = db_session.query(Job).get(job_id)
        if not job or (user_id and job.user_id != user_id):
            return "Job Not Found", 404

        job.status = JobStatus.Executing.value
        job_run = JobRun(job_id=job_id,
                         type=JobRunType.Schedule.value)
        db_session.add(job_run)
        db_session.commit()

        emit('status', {'job_id': job_id,
                        'job_run_id': job_run.id,
                        'status': job.status},
             namespace='/socket',
             broadcast=True)
        path_to_job_files = get_path_to_job(JobType.PUBLISHED, job.user.api_key, str(job.id))
        executor.execute_and_stream_to_db(path_to_job_files, str(job.id), str(job_run.id))


@jobs_bp.route('/jobs/execute', methods=['POST'])
@auth.login_required
def run_job_by_schedule():
    """
    Executing job which was scheduled
    """
    job_id = request.json['job_id']
    logging.info(f"Running job {job_id} based on schedule")
    _run_job(job_id, JobRunType.Schedule.value)
    return f"Running job {job_id}", 200


@jobs_bp.route('/jobs/<job_id>/run', methods=['POST'])
@requires_auth
def run_job(job_id):
    """
    Executing job when triggered manually via UI
    """
    _run_job(job_id, JobRunType.RunButton.value, session['profile']['internal_user_id'])
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
    if not file:
        return Response('File not provided', 400)

    try:
        project_path = project.create(file, api_key, JobType.RUN)
    except project.ProjectValidationError as exc:
        return Response(str(exc), 400)

    logstream = executor.execute_and_stream_back(project_path, api_key)

    return Response(logstream)