from flask import Blueprint, jsonify
from flask_login import login_required

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
@login_required
def get_jobs():
    return jsonify(list(JOBS_BY_ID.values())), 200


@jobs_bp.route('/jobs/<job_id>', methods=['GET'])
@login_required
def get_job(job_id):
    return jsonify((JOBS_BY_ID[int(job_id)])), 200
