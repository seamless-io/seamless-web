import json
import os
from functools import wraps
from urllib.parse import urlencode

import jinja2
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import Flask, render_template, session, url_for, redirect, jsonify

from app_config import Config
from core import config
from core.apis.core.auth import CoreAuthError

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)

API_VERSION = '/api/v1'
CORE_API = '/core'
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

    from core.apis.client.jobs import jobs_bp
    app.register_blueprint(jobs_bp, url_prefix=API_VERSION)

    from core.apis.client.users import users_bp
    app.register_blueprint(users_bp, url_prefix=API_VERSION)

    from core.apis.core.jobs import core_jobs_bp
    app.register_blueprint(core_jobs_bp, url_prefix=CORE_API)

    from core.apis.core.users import core_users_bp
    app.register_blueprint(core_users_bp, url_prefix=CORE_API)

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
        session['profile'] = {
            'user_id': userinfo['sub'],
            'name': userinfo['name'],
            'picture': userinfo['picture']
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
