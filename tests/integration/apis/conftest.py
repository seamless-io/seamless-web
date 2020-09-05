import os
import copy
import runpy
import importlib

import pytest
from flask.testing import FlaskClient
from werkzeug.datastructures import Headers

import config
from application import application


class CLIClient(FlaskClient):

    def open(self, *args, **kwargs):
        auth_headers = {
            'Authorization': self._api_key
        }
        headers = kwargs.pop('headers', Headers())
        if 'Authorization' not in headers:
            # do not overwrite auth headers if provided
            headers.extend(auth_headers)

        kwargs['headers'] = headers
        return super().open(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        self._api_key = kwargs.pop("api_key", None)
        if not self._api_key:
            raise RuntimeError("CLI authorization realized via API key. "
                               "Please, provide `api_key` in order to use Test CLI Client")
        super().__init__(*args, **kwargs)

@pytest.fixture
def web_client(postgres, user_id, user_email):
    """
    Web client fixture. This fixture should be used when we are testing api's used by the frontend and complying
    with auth0 authentication
    """
    application.config['TESTING'] = True

    with application.test_client() as client:
        with client.session_transaction() as session:
            session['jwt_payload'] = session['profile'] = {
                'user_id': user_id,  # no matter what is in here
                'email': user_email,
                'internal_user_id': user_id
            }
        yield client


@pytest.fixture
def cli_client(user_api_key, user_id):  # we need to use `user_id` fixture here to create a user in the db
    """
    CLI client fixture. This fixture should be used when we are testing api's used by the CLI and using API key auth
    """
    application.config['TESTING'] = True
    application.test_client_class = CLIClient
    with application.test_client(api_key=user_api_key) as client:
        yield client


@pytest.fixture
def automation_client(user_id):  # we need to use `user_id` fixture here to create a user in the db
    """
    Automation client fixture. This fixutre should be used when we are testing endpoints called by our automation
    and using BasicAuth
    """
    application.config['TESTING'] = True

    env_back = copy.deepcopy(os.environ)

    os.environ['GITHUB_ACTIONS_PASSWORD'] = '123'
    os.environ['LAMBDA_PROXY_PASSWORD'] = '555'

    importlib.reload(config)  # for config module to fetch params from env

    with application.test_client() as client:
        yield client

    os.environ = env_back
    importlib.reload(config)
