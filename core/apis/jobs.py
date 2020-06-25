from flask import Blueprint, jsonify
from flask_login import login_required

jobs_bp = Blueprint('jobs', __name__)


@jobs_bp.route('/jobs', methods=['GET'])
@login_required
def get_jobs():
    jobs = [
        {
            'id': 1,
            'name': 'Send email with stocks to invest',
            'schedule': 'Every Monday, at 12:00 PM',
            'is_schedule_enabled': True,
            'status': 'New'},
        {
            'id': 2,
            'name': 'Find new apts on OLX',
            'schedule': 'Not scheduled',
            'is_schedule_enabled': False,
            'status': 'Ok'},
        {
            'id': 3,
            'name': 'Check train tickets',
            'schedule': 'Every minute',
            'is_schedule_enabled': True,
            'status': 'Failed'},
        {
            'id': 4,
            'name': 'Update database',
            'schedule': 'Every hour on weekday',
            'is_schedule_enabled': False,
            'status': 'Ok'}
    ]
    return jsonify(jobs), 200
