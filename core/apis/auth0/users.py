import logging
import os

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError

from core.api_key import generate_api_key
from core.apis.auth0.auth import requires_auth
from core.emails.client import send_welcome_email
from core.models import db_commit
from core.models.users import User
from core.telegram.client import notify_about_new_user
from core.web import get_db_session

auth_users_bp = Blueprint('auth_users', __name__)

logging.basicConfig(level='INFO')


def add_user_to_db(email):
    user = User(email=email,
                api_key=generate_api_key())
    db_session = get_db_session()
    db_session.add(user)
    db_commit()
    return user.id


@auth_users_bp.route('/users', methods=['POST'])
@requires_auth
def auth0_webhook():
    data = request.json
    logging.info('auth0_webhook')
    logging.info(data)

    user = data['user']
    context = data['context']
    email = user['email']

    if (context['stats']['loginsCount'] > 1) or (context['protocol'] == 'oauth2-refresh-token'):
        message = f'The user {email} signed in'
    else:
        try:
            user_id = add_user_to_db(email)
            message = f'New user {email} (id: {user_id}) signed up!'
            if os.getenv('STAGE', 'local') == 'prod':
                notify_about_new_user(email)
                send_welcome_email(email)
        except IntegrityError as e:
            if 'duplicate key value violates unique constraint "ix_users_email"' in str(e):
                message = f'The user {email} signed in using different method than during the signup'
            else:
                raise e

    logging.info(message)
    return jsonify({'message': message}), 200
