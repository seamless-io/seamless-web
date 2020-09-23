from flask import Blueprint, session, jsonify, Response

import core.services.workspace as workspace_service
from core.web import requires_auth
from helpers import row2dict

workspaces_bp = Blueprint('workspaces', __name__)


@workspaces_bp.route('/', methods=['GET'])
@requires_auth
def get_workspaces():
    user_id = session['profile']['user_id']
    workspaces = workspace_service.get_available_workspaces(user_id)
    rv = [row2dict(workspace) for workspace in workspaces]
    return jsonify(rv), 200


@workspaces_bp.route('/<workspace_id>/upgrade/<plan>', methods=['POST'])
@requires_auth
def upgrade_workspace(workspace_id, plan):
    user_id = session['profile']['user_id']
    try:
        workspace_service.upgrade_workspace(user_id, workspace_id, plan)
    except workspace_service.PlanChangeError as e:
        return Response(str(e), 400)
    return Response("Upgrade was successful", 200)


@workspaces_bp.route('/<workspace_id>/downgrade/<plan>', methods=['POST'])
@requires_auth
def downgrade_workspace(workspace_id, plan):
    user_id = session['profile']['user_id']
    try:
        workspace_service.downgrade_workspace(user_id, workspace_id, plan)
    except workspace_service.PlanChangeError as e:
        return Response(str(e), 400)
    return Response("Downgrade was successful", 200)


@workspaces_bp.route('/<workspace_id>/invite/<user_email>')
def invite_user(workspace_id, user_email):
    workspace_service.invite_user(user_email, workspace_id)
    return Response('OK', 200)


@workspaces_bp.route('/<workspace_id>/remove/<user_email>')
def remove_user(workspace_id, user_email):
    return Response('OK', 200)


@workspaces_bp.route('/<workspace_id>/accept/<accept_key>')
def accept_invintaion(workspace_id, accept_key):
    user_email = session['profile']['email']
    try:
        workspace_service.accept_invitation(user_email, workspace_id, accept_key)
    except workspace_service.InvitationError as e:
        return Response(str(e), 400)
    return Response('OK', 200)


@workspaces_bp.errorhandler(workspace_service.WorkspaceNotFound)
def handle_error(e):
    return jsonify(error=str(e)), 404
