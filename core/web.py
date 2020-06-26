import json
import os
from functools import wraps
from urllib.parse import urlencode

import jinja2
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import Flask, render_template, session, url_for, redirect

from config import Config

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)

API_VERSION = '/api/v1'
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

    from core.apis.jobs import jobs_bp
    app.register_blueprint(jobs_bp, url_prefix=API_VERSION)

    oauth = OAuth(app)

    auth0 = oauth.register(
        'auth0',
        client_id=os.environ.get('AUTH0_CLIENT_ID'),
        client_secret=os.environ.get('AUTH0_CLIENT_SECRET'),
        api_base_url=os.environ.get('AUTH0_BASE_URL'),
        access_token_url=os.environ.get('AUTH0_BASE_URL') + '/oauth/token',
        authorize_url=os.environ.get('AUTH0_BASE_URL') + '/authorize',
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
        return auth0.authorize_redirect(redirect_uri=os.environ.get('AUTH0_CALLBACK_URL', ),
                                        audience=None)

    @app.route('/logout')
    def logout():
        session.clear()
        params = {'returnTo': url_for('catch_all', _external=True), 'client_id': os.environ.get('AUTH0_CLIENT_ID')}
        return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

    @app.route('/', methods=['GET'])
    @app.route('/<path:path>', methods=['GET'])
    @requires_auth
    def catch_all(path=None, **kwargs):
        return render_template('index.html',
                               userinfo=session['profile'],
                               userinfo_pretty=json.dumps(session['jwt_payload'], indent=4))

    return app
