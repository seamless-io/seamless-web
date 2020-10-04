import logging
import os

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError

from core.apis.auth0.auth import requires_auth
from core.emails.client import send_welcome_email
from core.services import user as user_service
from core.telegram.client import notify_about_new_user

auth_users_bp = Blueprint('auth_users', __name__)

logging.basicConfig(level='INFO')


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
            user_id = user_service.create(email)
            message = f'New user {email} (id: {user_id}) signed up!'
            pricing_plan = context['request']['query'].get('pricing_plan')
            if os.getenv('STAGE', 'local') == 'prod':
                notify_about_new_user(email, pricing_plan)
                send_welcome_email(email)
        except IntegrityError as e:
            if 'duplicate key value violates unique constraint "ix_users_email"' in str(e):
                message = f'The user {email} signed in using different method than during the signup'
            else:
                raise e

    logging.info(message)
    return jsonify({'message': message}), 200
