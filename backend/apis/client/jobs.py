from flask import Blueprint, jsonify, session

from backend.db import session_scope
from backend.db.helpers import row2dict
from backend.db.models import Job, User, JobRun
from backend.db.models.job_runs import JobRunType
from backend.db.models.jobs import JobStatus
from backend.web import requires_auth
from job_executor import executor
from job_executor.project import get_path_to_job, JobType

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
        return jsonify(row2dict(db_session.query(Job).get(job_id))), 200


@jobs_bp.route('/jobs/<job_id>/run', methods=['POST'])
@requires_auth
def run_job(job_id):
    with session_scope() as db_session:
        job = db_session.query(Job).get(job_id)
        job.status = JobStatus.Executing.value
        job_run = JobRun(job_id=job_id,
                         type=JobRunType.RunButton.value)
        db_session.add(job_run)
        db_session.commit()

        path_to_job_files = get_path_to_job(JobType.PUBLISHED, job.user.api_key, str(job.id))
        executor.execute_and_stream_to_db(path_to_job_files, str(job.id), str(job_run.id))
        return f"Running job {job.name}", 200


@jobs_bp.route('/jobs/<job_id>/logs', methods=['GET'])
@requires_auth
def get_job_logs(job_id: str):
    with session_scope() as db_session:
        job = db_session.query(Job).get(job_id)
        job_runs = job.get_sorted_job_runs()
        if not job_runs:
            return "No logs yet, please run the job at least once.", 200

        # Hardcode to return only the last run logs
        job_run = job_runs[-1]
        logs = [row2dict(log_record) for log_record in job_run.logs]

        return jsonify(logs), 200
