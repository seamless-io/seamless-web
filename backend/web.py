import json
import logging
import os
from functools import wraps
from urllib.parse import urlencode

import jinja2
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import Flask, render_template, session, url_for, redirect, jsonify

from app_config import Config
from backend import config
from backend.apis.auth0.auth import CoreAuthError
from backend.db import get_session
from backend.db.models import User

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)

CLIENT_API = '/api/v1'
AUTH_API = '/auth'
CLI_API = '/cli'
SCHEDULE_API = '/schedule'
APP_DIR = os.path.dirname(os.path.realpath(__file__))
TEMPLATES_DIR = os.path.join(APP_DIR, '../static/')
CLIENT_DIR = os.path.join(APP_DIR, '../static/')


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated


def create_app():
    app = Flask(__name__, static_folder=CLIENT_DIR, static_url_path='/static')
    app.config.from_object(Config)
    app.jinja_loader = jinja2.FileSystemLoader([TEMPLATES_DIR, CLIENT_DIR])

    from backend.apis.client.jobs import jobs_bp
    app.register_blueprint(jobs_bp, url_prefix=CLIENT_API)

    from backend.apis.client.users import user_bp
    app.register_blueprint(user_bp, url_prefix=CLIENT_API)

    from backend.apis.auth0.users import auth_users_bp
    app.register_blueprint(auth_users_bp, url_prefix=AUTH_API)

    from backend.apis.schedule.schedule_events import schedule_events_bp
    app.register_blueprint(schedule_events_bp, url_prefix=SCHEDULE_API)

    oauth = OAuth(app)

    auth0 = oauth.register(
        'auth0',
        client_id=config.AUTH0_CLIENT_ID,
        client_secret=config.AUTH0_CLIENT_SECRET,
        api_base_url=config.AUTH0_BASE_URL,
        access_token_url=config.AUTH0_BASE_URL + '/oauth/token' if config.AUTH0_BASE_URL else '',
        authorize_url=config.AUTH0_BASE_URL + '/authorize' if config.AUTH0_BASE_URL else '',
        client_kwargs={
            'scope': 'openid profile email',
        },
    )

    @app.route('/callback')
    def callback_handling():
        auth0.authorize_access_token()
        resp = auth0.get('userinfo')
        userinfo = resp.json()

        session['jwt_payload'] = userinfo

        internal_user_id = User.get_user_from_email(userinfo['email'], get_session()).id

        session['profile'] = {
            'user_id': userinfo['sub'],
            'email': userinfo['email'],
            'internal_user_id': internal_user_id
        }
        return redirect('/')

    @app.route('/login')
    def login():
        return auth0.authorize_redirect(redirect_uri=config.AUTH0_CALLBACK_URL,
                                        audience=None)

    @app.route('/logout')
    def logout():
        session.clear()
        params = {'returnTo': url_for('catch_all', _external=True), 'client_id': config.AUTH0_CLIENT_ID}
        return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

    @app.route('/health-check')
    def health_check():
        return "Success", 200

    # This handles auth errors on the "core" API (/core)
    @app.errorhandler(CoreAuthError)
    def handle_auth_error(ex):
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        return response

    # Catch all to server the react app
    @app.route('/', methods=['GET'])
    @app.route('/<path:path>', methods=['GET'])
    @requires_auth
    def catch_all(path=None, **kwargs):
        return render_template('index.html',
                               userinfo=session['profile'],
                               userinfo_pretty=json.dumps(session['jwt_payload'], indent=4))

    return app
