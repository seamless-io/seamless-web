from flask import Blueprint, jsonify, request, Response

from backend.db import session_scope
from backend.db.models import Job, User
from job_executor import project, executor
from job_executor.project import ProjectType

cli_bp = Blueprint('cli', __name__)


@cli_bp.route('/publish', methods=['POST'])
def create_job():
    api_key = request.headers.get('Authorization')
    if not api_key:
        return Response('Not authorized request', 401)

    job_name = request.args.get('name')
    cron_schedule = request.args.get('schedule')

    print(job_name)
    print(cron_schedule)

    with session_scope() as session:
        user = User.get_user_from_api_key(api_key, session)
        job_attributes = {
            'name': job_name,
            'user_id': user.id
        }
        if cron_schedule:
            job_attributes.update({"schedule": cron_schedule})
        job = Job(**job_attributes)
        session.add(job)
        session.commit()
        return jsonify({'job_id': job.id}), 200


@cli_bp.route('/run', methods=['POST'])
def run() -> Response:
    api_key = request.headers.get('Authorization')
    if not api_key:
        return Response('Not authorized request', 401)

    file = request.files.get('seamless_project')
    if not file:
        return Response('File not provided', 400)

    try:
        project_path = project.create(file, api_key, ProjectType.RUN)
    except project.ProjectValidationError as exc:
        return Response(str(exc), 400)

    logstream = executor.execute(project_path, api_key)

    return Response(logstream)
