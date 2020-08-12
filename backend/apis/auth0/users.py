import logging

import requests
from flask import Blueprint, request, jsonify
from sentry_sdk import capture_exception

from backend.api_key import generate_api_key
from backend.apis.auth0.auth import requires_auth
from backend.db import session_scope
from backend.db.models import User
from config import TELEGRAM_BOT_API_KEY, TELEGRAM_CHANNEL_ID

auth_users_bp = Blueprint('auth_users', __name__)

logging.basicConfig(level='INFO')


def add_user_to_db(email):
    with session_scope() as session:
        user = User(email=email,
                    api_key=generate_api_key())
        session.add(user)
        session.commit()
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
def create_user():
    logging.info(request.json)
    email = request.json['email']
    user_id = add_user_to_db(email)
    send_telegram_message(email)
    return jsonify({'user_id': user_id}), 200
