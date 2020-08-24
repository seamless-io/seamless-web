import uuid

import docker
import pytest


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
