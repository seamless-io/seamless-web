from flask import Blueprint, jsonify


tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = [
        {'name': 'task 1'},
        {'name': 'task 2'}
    ]
    return jsonify(tasks), 200
