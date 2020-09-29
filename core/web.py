import json
import os
from functools import wraps
from time import sleep
from urllib.parse import urlencode

import jinja2
from authlib.integrations.flask_client import OAuth
from flask import Flask, render_template, session, url_for, redirect, jsonify, request
from sqlalchemy.orm.exc import NoResultFound

from app_config import Config
from core.apis.auth0.auth import CoreAuthError
from core.models import get_db_session
from core.models.users import User
from core.services.workspace import get_user_personal_workspace

CLIENT_API = '/api/v1'
AUTH_API = '/auth'
STRIPE_API = '/stripe'
APP_DIR = os.path.dirname(os.path.realpath(__file__))
TEMPLATES_DIR = os.path.join(APP_DIR, '../static/')
CLIENT_DIR = os.path.join(APP_DIR, '../static/')


class CannotFindSignedUpUserException(Exception):
    pass


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
            return redirect('/login')

        # TODO this block is needed to invalidate old sessions because
        #  I have changed the session object recently.
        #  After sufficient time passes this could be safely deleted
        #  Added on Sep 18 2020
        if 'internal_user_id' in session:
            return redirect('/logout')

        return f(*args, **kwargs)

    return decorated


def create_app():
    app = Flask(__name__, static_folder=CLIENT_DIR, static_url_path='/static')
    app.config.from_object(Config)
    app.jinja_loader = jinja2.FileSystemLoader([TEMPLATES_DIR, CLIENT_DIR])

    from core.apis.jobs import jobs_bp
    app.register_blueprint(jobs_bp, url_prefix=CLIENT_API)

    from core.apis.users import user_bp
    app.register_blueprint(user_bp, url_prefix=CLIENT_API)

    from core.apis.marketplace import marketplace_bp
    app.register_blueprint(marketplace_bp, url_prefix=CLIENT_API)

    from core.apis.workspaces import workspaces_bp
    app.register_blueprint(workspaces_bp, url_prefix=CLIENT_API + '/workspaces')

    from core.apis.auth0.users import auth_users_bp
    app.register_blueprint(auth_users_bp, url_prefix=AUTH_API)

    from core.apis.stripe import stripe_bp
    app.register_blueprint(stripe_bp, url_prefix=STRIPE_API)

    oauth = OAuth(app)

    auth0 = oauth.register(
        'auth0',
        client_id=os.getenv('AUTH0_CLIENT_ID'),
        client_secret=os.getenv('AUTH0_CLIENT_SECRET'),
        api_base_url=os.getenv('AUTH0_BASE_URL'),
        access_token_url=os.getenv('AUTH0_BASE_URL') + '/oauth/token' if os.getenv('AUTH0_BASE_URL') else '',
        authorize_url=os.getenv('AUTH0_BASE_URL') + '/authorize' if os.getenv('AUTH0_BASE_URL') else '',
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

        user_id = None
        for i in range(3):  # Try 3 times
            try:
                user_id = User.get_user_from_email(userinfo['email'], get_db_session()).id
            except NoResultFound:
                sleep(1)  # when the user is signing up, we write asynchronously to the db, so we may need a delay
            if user_id:
                break

        if not user_id:
            raise CannotFindSignedUpUserException(f"We cannot find the user {userinfo} in our database."
                                                  f"Maybe the user registration endpoint failed.")

        workspace = get_user_personal_workspace(user_id)

        session['profile'] = {
            'auth0_user_id': userinfo['sub'],
            'email': userinfo['email'],
            'user_id': user_id,
            'workspace_id': str(workspace.id)  # Set Personal workspace by default
        }
        return redirect('/')

    @app.route('/login')
    def login():
        return auth0.authorize_redirect(redirect_uri=os.getenv('AUTH0_CALLBACK_URL'),
                                        audience=None,
                                        pricing_plan=request.args.get('pricing_plan', 'free'))

    @app.route('/debug-sentry')
    def trigger_error():
        1 / 0

    @app.route('/logout')
    def logout():
        session.clear()
        params = {'returnTo': url_for('catch_all', _external=True), 'client_id': os.getenv('AUTH0_CLIENT_ID')}
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

    # Catch all to serve the react app
    @app.route('/', methods=['GET'])
    @app.route('/<path:path>', methods=['GET'])
    @requires_auth
    def catch_all(path=None, **kwargs):
        return render_template('index.html',
                               userinfo=session['profile'],
                               userinfo_pretty=json.dumps(session['jwt_payload'], indent=4))

    return app
