import os
import uuid
import subprocess
import time

import docker
import pytest
from flask.testing import FlaskClient
from werkzeug.datastructures import Headers

from application import application
from core.models import get_db_session, db_commit, User


SECOND = 1000000000


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


def wait_on_condition(condition, delay=0.1, timeout=40):
    start_time = time.time()
    while not condition():
        if time.time() - start_time > timeout:
            raise AssertionError("Timeout: %s" % condition)
        time.sleep(delay)


def wait_on_health_status(client, container_id, status):
    def condition():
        res = client.containers.get(container_id).attrs
        return res['State']['Health']['Status'] == status
    return wait_on_condition(condition)


@pytest.fixture(scope='session')
def docker_client():
    return docker.from_env(version='auto')


@pytest.fixture(scope='session')
def session_id():
    """Unique session identifier, random string."""
    return str(uuid.uuid4())


@pytest.fixture(scope='session')
def postgres(docker_client, session_id):
    image = "postgres:10.9"
    name = "postgres-test-%s" % session_id

    db_user = 'postgres_default'
    db_password = 'postgres_root'
    db_name = 'seamless'

    img = docker_client.images.pull(image)

    container = docker_client.containers.run(img, detach=True, name=name,
                                             ports={'5432': None},
                                             environment={
                                                 'POSTGRES_USER': db_user,
                                                 'POSTGRES_PASSWORD': db_password,
                                                 'POSTGRES_DB': db_name
                                             },
                                             healthcheck={
                                                 'test': 'pg_isready',
                                                 'interval': 2 * SECOND,
                                                 'timeout': 2 * SECOND,
                                                 'retries': 3
                                             })
    wait_on_health_status(docker_client, container.id, 'healthy')

    attrs = docker_client.containers.get(container.id).attrs

    host = attrs['NetworkSettings']['Ports']['5432/tcp'][0]['HostIp']
    port = attrs['NetworkSettings']['Ports']['5432/tcp'][0]['HostPort']


    db_env = {
        'SEAMLESS_DB_HOST': host,
        'SEAMLESS_DB_PORT': port,
        'SEAMLESS_DB_USER': db_user,
        'SEAMLESS_DB_PASSWORD': db_password,
        'SEAMLESS_DB_NAME': db_name
    }

    env_back = os.environ
    os.environ.update(db_env)

    print(db_env)

    try:
        # applying migrations to the database
        rv = subprocess.run(['alembic', 'upgrade', 'head'], env=os.environ)
        assert rv.returncode == 0, "Migration should finish succesfully"

        yield db_env

    finally:

        # Clean up
        # Remove the docker container
        container.remove(force=True)

        # Remove the volumes
        for volume_d in attrs['Mounts']:
            volume_name = volume_d['Name']
            vol = docker_client.volumes.get(volume_name)
            vol.remove(force=True)

        # rolling back environment
        os.environ = env_back


@pytest.fixture
def user_email():
    return 'testuser@seamlesscloud.io'


@pytest.fixture
def user_api_key():
    return '123'


@pytest.fixture
def user_id(postgres, user_email, user_api_key):
    user = User(email=user_email, api_key=user_api_key)
    get_db_session().add(user)
    db_commit()

    yield user.id

    get_db_session().delete(user)
    db_commit()


@pytest.fixture
def web_client(postgres, user_id, user_email):
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
    application.config['TESTING'] = True
    application.test_client_class = CLIClient
    with application.test_client(api_key=user_api_key) as client:
        yield client
