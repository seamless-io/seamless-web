from flask import Blueprint, jsonify, session

from backend.db import session_scope
from backend.db.helpers import row2dict
from backend.db.models import Job, User
from backend.web import requires_auth

jobs_bp = Blueprint('jobs', __name__)


@jobs_bp.route('/jobs', methods=['GET'])
@requires_auth
def get_jobs():
    email = session['profile']['email']
    with session_scope() as db_session:
        user = User.get_user_from_email(email, db_session)
        print(user.jobs)
        jobs = [row2dict(job) for job in user.jobs]
        print(jobs)
        return jsonify(jobs), 200


@jobs_bp.route('/jobs/<job_id>', methods=['GET'])
@requires_auth
def get_job(job_id):
    with session_scope() as session:
        return jsonify(row2dict(session.query(Job).get(job_id))), 200
