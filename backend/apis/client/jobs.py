from flask import Blueprint, jsonify, session, request
from flask_socketio import emit

from backend.db import session_scope
from backend.db.helpers import row2dict
from backend.db.models import Job, User, JobRun
from backend.db.models.job_runs import JobRunType
from backend.db.models.jobs import JobStatus
from backend.web import requires_auth
from job_executor import executor
from job_executor.project import get_path_to_job, JobType
from job_executor.scheduler import enable_job_schedule, disable_job_schedule

jobs_bp = Blueprint('jobs', __name__)

TIMESTAMP_FOR_LOGS_FORMAT = "%m_%d_%Y_%H_%M_%S_%f"


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


# TODO: figure out auth
@jobs_bp.route('/jobs/execute', methods=['POST'])  # events from SQS sent to this endpoint (see beanstalk config)
def run_job_by_schedule():
    job_id = request.json['job_id']
    with session_scope() as db_session:
        job = db_session.query(Job).get(job_id)
        if not job:
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
        return f"Running job {job.name}", 200


@jobs_bp.route('/jobs/<job_id>/run', methods=['POST'])
@requires_auth
def run_job(job_id):
    with session_scope() as db_session:
        job = db_session.query(Job).get(job_id)
        if not job or job.user_id != session['profile']['internal_user_id']:
            return "Job Not Found", 404
        job.status = JobStatus.Executing.value
        job_run = JobRun(job_id=job_id,
                         type=JobRunType.RunButton.value)
        db_session.add(job_run)
        db_session.commit()

        emit('status', {'job_id': job_id,
                        'job_run_id': job_run.id,
                        'status': job.status},
             namespace='/socket',
             broadcast=True)

        path_to_job_files = get_path_to_job(JobType.PUBLISHED, job.user.api_key, str(job.id))
        executor.execute_and_stream_to_db(path_to_job_files, str(job.id), str(job_run.id))
        return f"Running job {job.name}", 200


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
