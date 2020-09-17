import logging

from flask import Blueprint, request

from core.apis.auth0.auth import requires_auth
from core.services.user import sign_up, UserAlreadyExists

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
        logging.info(f'The user {email} signed in')
    else:
        try:
            sign_up(email, context['request']['query'].get('pricing_plan'))
        except UserAlreadyExists:
            logging.info(f'The user {email} signed in using different method than during the signup')

    return "Success", 200
