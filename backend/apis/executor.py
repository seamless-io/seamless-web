"""
Provides an API which receive job data and executes it.
The information about the job received from SQS queue: scheduled-to-execute.fifo
"""
from flask import Blueprint, jsonify, session, request

from job_executor import executor


exec_bp = Blueprint('executor', __name__)


# TODO: provide AUTH!
@exec_bp.route('/execute', methods=['POST'])
def execute_project():
    data = request.json()
    # TODO: programmatically tie the structure for data with one
    # provided in `job_executor/executor.py` file when writing to queue
    project_path = data['project_path']
    # executor.execute_and_stream_to_db(project_path, ...)
    return jsonify({}), 200
