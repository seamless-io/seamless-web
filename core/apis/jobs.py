from flask import Blueprint, jsonify, request

from core.db import get_session, session_scope
from core.db.models import Job
from core.web import requires_auth

jobs_bp = Blueprint('jobs', __name__)

JOBS_BY_ID = {
    1: {
        'id': 1,
        'name': 'Send email with stocks to invest',
        'schedule': 'Every Monday, at 12:00 PM',
        'is_schedule_enabled': True,
        'status': 'New'},
    2: {
        'id': 2,
        'name': 'Find new apts on OLX',
        'schedule': 'Not scheduled',
        'is_schedule_enabled': False,
        'status': 'Ok'},
    3: {
        'id': 3,
        'name': 'Check train tickets',
        'schedule': 'Every minute',
        'is_schedule_enabled': True,
        'status': 'Failed'},
    4: {
        'id': 4,
        'name': 'Update database',
        'schedule': 'Every hour on weekday',
        'is_schedule_enabled': False,
        'status': 'Ok'}
}


@jobs_bp.route('/jobs', methods=['GET'])
@requires_auth
def get_jobs():
    return jsonify(list(JOBS_BY_ID.values())), 200


@jobs_bp.route('/jobs/<job_id>', methods=['GET'])
@requires_auth
def get_job(job_id):
    return jsonify((JOBS_BY_ID[int(job_id)])), 200


@jobs_bp.route('/jobs', methods=['POST'])
@requires_auth
def create_job():
    with session_scope() as session:
        user_id = 1  # get from api key
        job = Job(**request.json, user_id=user_id)
        session.add(job)
        session.commit()
        return jsonify({'job_id': job.id}), 200
