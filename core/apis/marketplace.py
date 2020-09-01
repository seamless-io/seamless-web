import logging

from flask import Blueprint, request, Response, jsonify, session
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

import helpers
from config import GITHUB_ACTIONS_PASSWORD, DEFAULT_CRON_SCHEDULE, DEFAULT_ENTRYPOINT, DEFAULT_REQUIREMENTS
from core.web import requires_auth
import core.services.job as job_service
import core.services.user as user_service
import core.services.marketplace as marketplace_service
from helpers import row2dict
from job_executor import project

marketplace_bp = Blueprint('marketplace', __name__)

logging.basicConfig(level='INFO')

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    """
    We are going to authenticate github_actions using hardcoded password
    """
    if username == 'github_actions' and check_password_hash(
            generate_password_hash(GITHUB_ACTIONS_PASSWORD), password):
        return username


@marketplace_bp.route('/marketplace', methods=['POST'])
@auth.login_required
def update_marketplace():
    logging.info("Updating the marketplace")
    templates_package = request.files.get('templates')
    if not templates_package:
        return Response('File not provided', 400)
    marketplace_service.update_templates(templates_package)
    return "Success", 200


@marketplace_bp.route('/templates', methods=['GET'])
@requires_auth
def get_templates():
    templates = marketplace_service.get_templates()
    rv = [row2dict(template) for template in templates]
    return jsonify(rv), 200


@marketplace_bp.route('/templates/<template_id>', methods=['GET'])
@requires_auth
def get_template(template_id):
    job = marketplace_service.get_template(template_id)
    return jsonify(row2dict(job)), 200


@marketplace_bp.route('/templates/<template_id>/create_job', methods=['POST'])
@requires_auth
def create_job_from_template(template_id):
    template = marketplace_service.get_template(template_id)
    template_file = marketplace_service.get_template_package(template_id)
    try:
        job, is_existing = job_service.publish(
            template.name,  # TODO check if name already exists
            DEFAULT_CRON_SCHEDULE,
            DEFAULT_ENTRYPOINT,
            DEFAULT_REQUIREMENTS,
            user_service.get_by_id(session['profile']['internal_user_id']),
            template_file,
            schedule_is_active=False
        )
    except job_service.JobsQuotaExceededException as e:
        return Response(str(e), 400)  # TODO: ensure that error code is correct
    except project.ProjectValidationError as e:
        return Response(str(e), 400)  # TODO: ensure that error code is correct
    except helpers.InvalidCronException as e:
        return Response(str(e), 400)  # TODO: ensure that error code is correct

    return jsonify({'job_id': job.id}), 200


@marketplace_bp.errorhandler(marketplace_service.JobTemplateNotFoundException)
def handle_error(e):
    return jsonify(error=str(e)), 404
