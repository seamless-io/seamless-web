import logging

from flask import Blueprint, request, jsonify

from backend.api_key import generate_api_key
from backend.apis.auth0.auth import requires_auth
from backend.db import session_scope
from backend.db.models import User

auth_users_bp = Blueprint('auth_users', __name__)

logging.basicConfig(level='INFO')


@auth_users_bp.route('/users', methods=['POST'])
@requires_auth
def create_user():
    logging.info(request.json)
    with session_scope() as session:
        user = User(email=request.json['email'],
                    api_key=generate_api_key())
        session.add(user)
        session.commit()
        return jsonify({'user_id': user.id}), 200
