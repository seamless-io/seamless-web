import logging

from flask import Blueprint, jsonify, request

from core.db import session_scope
from core.web import requires_auth
from core.db.models import User

api_key_bp = Blueprint('jobs', __name__)

logging.basicConfig(level='INFO')


@api_key_bp.route('/api-key', methods=['GET'])
@requires_auth
def get_api_key():
    email = request.args.get('email')
    try:
        with session_scope() as session:
            user = session.query(User).filter(User.email == email).one_or_none()
            if user:
                return jsonify({'api_key': user.api_key}), 200
            return jsonify({'message': 'Unable to find a user'}), 404
    except Exception as e:
        logging.exception(e)
        logging.exception(request.data.decode('utf-8'))
        return jsonify({'message': 'Unable to get an api key'}), 500
