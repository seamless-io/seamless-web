import logging

from flask import Blueprint, request, jsonify

from backend.api_key import generate_api_key
from backend.apis.auth0.auth import requires_auth
from backend.db import session_scope
from backend.db.models import User

auth_users_bp = Blueprint('auth_users', __name__)

logging.basicConfig(level='INFO')


def add_user_to_db(email):
    with session_scope() as session:
        user = User(email=email,
                    api_key=generate_api_key())
        session.add(user)
        session.commit()
        return user.id


@auth_users_bp.route('/users', methods=['POST'])
@requires_auth
def create_user():
    logging.info(request.json)
    user_id = add_user_to_db(request.json['email'])
    return jsonify({'user_id': user_id}), 200
