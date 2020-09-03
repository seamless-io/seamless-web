import os
import uuid
import subprocess
import time

import docker
import pytest


SECOND = 1000000000


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
