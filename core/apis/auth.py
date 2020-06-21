import logging

from flask import Blueprint, jsonify, redirect, url_for, request
from flask_login import login_required, logout_user, login_user

from core.db import session_scope
from core.db.models import User

logging.basicConfig(level='INFO')

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        response = request.get_json()
    except Exception as e:
        logging.exception(e)
        logging.info(request.data.decode("utf-8"))
        return jsonify({'error': str(e),
                        'message': 'Unable to parse JSON.'}), 400

    try:
        email = response['email']
        password = response['password']
        remember = response['remember']

        with session_scope() as session:
            user = session.query(User).filter_by(email=email.lower()).first()
            if user is not None and user.verify_password(password):
                login_user(user, remember)
                next = request.args.get('next')
                if next is None or not next.startswith('/'):
                    next = '/'
                return redirect(next)
            return jsonify({'message': 'User is unauthorized.'}), 401
    except Exception as e:
        logging.exception(e)
        logging.info(request.data.decode("utf-8"))
        return jsonify({'error': str(e),
                        'message': 'Unable to log in a user.'}), 500


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/', code=302)
