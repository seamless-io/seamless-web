import os

import jinja2
from flask import Flask, render_template

API_VERSION = '/api/v1'
APP_DIR = os.path.join(os.path.realpath(__file__))
TEMPLATES_DIR = os.path.join(APP_DIR, '../static')
CLIENT_DIR = os.path.join(APP_DIR, '../static')


def create_app():
    app = Flask(__name__, static_folder=CLIENT_DIR, static_url_path='/static')
    app.jinja_loader = jinja2.FileSystemLoader([TEMPLATES_DIR, CLIENT_DIR])

    from core.apis.tasks import tasks_bp
    app.register_blueprint(tasks_bp, url_prefix=API_VERSION)

    @app.route('/', methods=['GET'])
    @app.route('/<path:path>', methods=['GET'])
    def catch_all(path=None, **kwargs):
        return render_template('index.html')

    return app
