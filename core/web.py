import os

import jinja2
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_login import LoginManager

from config import Config

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)

API_VERSION = '/api'
APP_DIR = os.path.dirname(os.path.realpath(__file__))
TEMPLATES_DIR = os.path.join(APP_DIR, '../static/')
CLIENT_DIR = os.path.join(APP_DIR, '../static/')

login_manager = LoginManager()
login_manager.login_view = '/login'


def create_app():
    app = Flask(__name__, static_folder=CLIENT_DIR, static_url_path='/static')
    app.config.from_object(Config)
    app.jinja_loader = jinja2.FileSystemLoader([TEMPLATES_DIR, CLIENT_DIR])
    login_manager.init_app(app)

    from core.apis.tasks import tasks_bp
    app.register_blueprint(tasks_bp, url_prefix=API_VERSION)

    from core.apis.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    @app.route('/', methods=['GET'])
    @app.route('/<path:path>', methods=['GET'])
    def catch_all(path=None, **kwargs):
        return render_template('index.html')

    return app
