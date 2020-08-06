import uuid
from unittest.mock import patch

import docker
import pytest

from core.api_key import generate_api_key
from core.models import session_scope
from core.models.users import User
from core.helpers import row2dict

NUMBER_OF_TEST_USERS = 2
DB_PREFIX = "INTEGRATION_TEST"


@pytest.fixture(scope="session")
def test_users():
    with patch('core.db.DB_PREFIX', DB_PREFIX):
        with session_scope() as db_session:
            users = [User(email=f"{i}@loadtest.com", api_key=generate_api_key())
                     for i in range(NUMBER_OF_TEST_USERS)]
            for user in users:
                db_session.add(user)
            db_session.commit()

            yield [row2dict(user) for user in users]

            for user in users:
                db_session.delete(user)
            db_session.commit()


# @pytest.fixture(scope='session')
# def docker_client():
#     return docker.from_env(version='auto')


@pytest.fixture(scope='session')
def session_id():
    """Unique session identifier, random string."""
    return str(uuid.uuid4())


# @pytest.fixture(scope='session')
# def postgres(docker_client, session_id):
#     image = "postgres:10.9"
#     name = "postgres-test-%s" % session_id
#     img = docker_client.images.pull(image)

#     container = docker_client.containers.run(img, detach=True, name=name,
#                                              ports={'5432': None})
#     attrs = docker_client.containers.get(container.id).attrs

#     yield

#     # Clean up
#     # Remove the docker container
#     container.remove(force=True)

#     # Remove the volumes
#     for volume_d in attrs['Mounts']:
#         volume_name = volume_d['Name']
#         vol = docker_client.volumes.get(volume_name)
#         vol.remove(force=True)
