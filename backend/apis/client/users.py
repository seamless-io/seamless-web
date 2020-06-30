import logging

from flask import Blueprint, jsonify, request, session

from backend.db import session_scope
from backend.web import requires_auth
from backend.db.models import User

user_bp = Blueprint('user', __name__)

logging.basicConfig(level='INFO')


@user_bp.route('/user', methods=['GET'])
@requires_auth
def get_user_info():
    email = session['profile']['email']
    try:
        with session_scope() as db_session:
            user = User.get_user_from_email(email, db_session)
            if user:
                return jsonify({'email': user.email,
                                'api_key': user.api_key}), 200
            return jsonify({'message': 'Unable to find a user'}), 404
    except Exception as e:
        logging.exception(e)
        logging.exception(request.data.decode('utf-8'))
        return jsonify({'message': 'Unable to get an api key'}), 500
