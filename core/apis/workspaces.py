from flask import Blueprint, session, jsonify

from core.services.workspace import get_available_workspaces
from core.web import requires_auth
from helpers import row2dict

workspaces_bp = Blueprint('workspaces', __name__)


@workspaces_bp.route('/workspaces', methods=['GET'])
@requires_auth
def get_workspaces():
    user_id = session['profile']['user_id']
    workspaces = get_available_workspaces(user_id)
    rv = [row2dict(workspace) for workspace in workspaces]
    return jsonify(rv), 200
