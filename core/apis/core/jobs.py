from flask import Blueprint, jsonify, request

from core.apis.core.auth import requires_auth
from core.db import session_scope
from core.db.models import Job

core_jobs_bp = Blueprint('core_jobs', __name__)


@core_jobs_bp.route('/jobs', methods=['POST'])
@requires_auth
def create_job():
    with session_scope() as session:
        user_id = 1  # get from api key
        job = Job(**request.json, user_id=user_id)
        session.add(job)
        session.commit()
        return jsonify({'job_id': job.id}), 200
