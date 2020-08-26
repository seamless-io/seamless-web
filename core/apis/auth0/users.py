import logging

import requests
from flask import Blueprint, request, jsonify
from sentry_sdk import capture_exception
from sqlalchemy.exc import IntegrityError

from core.api_key import generate_api_key
from core.apis.auth0.auth import requires_auth
from core.models.users import User
from config import TELEGRAM_BOT_API_KEY, TELEGRAM_CHANNEL_ID, STAGE
from core.web import get_db_session

auth_users_bp = Blueprint('auth_users', __name__)

logging.basicConfig(level='INFO')


def add_user_to_db(email):
    user = User(email=email,
                api_key=generate_api_key())
    db_session = get_db_session()
    db_session.add(user)
    db_session.commit()
    return user.id


def send_telegram_message(email):
    resp = requests.get(f'https://api.telegram.org/bot{TELEGRAM_BOT_API_KEY}/sendMessage',
                        params={'chat_id': TELEGRAM_CHANNEL_ID,
                                'text': f"Fuck yeah, new user {email}"})
    try:
        resp.raise_for_status()
    except Exception as e:
        logging.error(e)
        capture_exception(e)


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
        except IntegrityError as e:
            if 'duplicate key value violates unique constraint "ix_users_email"' in str(e):
                message = f'The user {email} signed in using different method than during the signup'
            else:
                raise e
        if STAGE == 'prod':
            send_telegram_message(email)

    logging.info(message)
    return jsonify({'message': message}), 200
