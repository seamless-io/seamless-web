import logging

from flask import Blueprint, request, jsonify

from core.api_key import generate_api_key
from core.apis.core.auth import requires_auth
from core.db import session_scope
from core.db.models import User

core_users_bp = Blueprint('core_users', __name__)

logging.basicConfig(level='INFO')


@core_users_bp.route('/users', methods=['POST'])
@requires_auth
def create_user():
    logging.info(request.data)
    with session_scope() as session:
        user = User(email=request.data['email'],
                    api_key=generate_api_key())
        session.add(user)
        session.commit()
        return jsonify({'user_id': user.id}), 200
