from flask import Blueprint, request

from core.apis.core.auth import requires_auth

core_users_bp = Blueprint('core_users', __name__)


@core_users_bp.route('/users', methods=['POST'])
@requires_auth
def create_user():
    print(request.data)
    return 'Success', 200
