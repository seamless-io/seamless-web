from flask import Blueprint, jsonify
from flask_login import login_required

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    tasks = [
        {'name': 'task 1'},
        {'name': 'task 2'}
    ]
    return jsonify(tasks), 200
