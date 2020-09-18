import copy
import io
import os
import subprocess
import tarfile
import time
import uuid

import boto3
import docker
import pytest
import pytest_localstack

from constants import DEFAULT_ENTRYPOINT, DEFAULT_REQUIREMENTS
from core.models import get_db_session, db_commit, User, Workspace
from core.models.workspaces import Plan
from core.services.marketplace import JOB_TEMPLATES_S3_BUCKET
from job_executor import project

SECOND = 1000000000


localstack = pytest_localstack.patch_fixture(services=["s3", "events"],
                                             scope='session',
                                             autouse=True,
                                             localstack_version='0.11.4')


@pytest.fixture(scope='session', autouse=True)
def lambda_proxy_env(localstack):
    """
    We use LAMBDA_PROXY_NAME and LAMBDA_PROXY_ARN while creating an event
    """
    os_back = copy.deepcopy(os.environ)

    os.environ['LAMBDA_PROXY_NAME'] = 'proxy_lambda_name'
    os.environ['LAMBDA_PROXY_ARN'] = 'proxy_lambda_arn'

    yield

    os.envion = os_back


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

    env_back = copy.deepcopy(os.environ)
    os.environ.update(db_env)

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

    plan = Plan.Personal.value
    workspace = Workspace(owner_id=user.id, name=plan, plan=plan, subscription_is_active=True)
    get_db_session().add(workspace)
    db_commit()

    yield user.id

    get_db_session().delete(user)
    get_db_session().delete(workspace)
    db_commit()


@pytest.fixture
def job_name():
    return 'Integration test job name'


@pytest.fixture
def job_entrypoint():
    # from tests/test_project
    return 'function.py'


@pytest.fixture
def job_requirements():
    # from tests/test_project
    return 'custom_requirements.txt'


@pytest.fixture(scope='session', autouse=True)
def create_s3_bucket_for_user_projects(localstack):
    s3 = boto3.client('s3')
    s3.create_bucket(Bucket=project.USER_PROJECTS_S3_BUCKET)


@pytest.fixture(scope='session', autouse=True)
def create_s3_bucket_for_templates(localstack):
    s3 = boto3.client('s3')
    s3.create_bucket(Bucket=JOB_TEMPLATES_S3_BUCKET)


@pytest.fixture
def archived_project():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    folder_to_archive = os.path.join(dir_path, '..', 'test_project', '.')

    handler = io.BytesIO()
    with tarfile.open(fileobj=handler, mode="w:gz") as tar:
        tar.add(folder_to_archive, arcname='.')
        tar.close()

    handler.seek(0)  # going back to the start after writing into it
    return handler


@pytest.fixture
def archived_templates_repo():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    template_files = os.path.join(dir_path, '..', 'marketplace_templates_files', '.')

    handler = io.BytesIO()
    with tarfile.open(fileobj=handler, mode="w:gz") as tar:
        tar.add(template_files, arcname='.')
        tar.close()

    handler.seek(0)
    yield handler


@pytest.fixture
def archived_project_no_requirements():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    folder_to_archive = os.path.join(dir_path, '..', 'test_project_no_requirements')

    handler = io.BytesIO()
    with tarfile.open(fileobj=handler, mode="w:gz") as tar:
        tar.add(folder_to_archive, arcname='.')
        tar.close()

    handler.seek(0)  # going back to the start after writing into it
    return handler


@pytest.fixture
def published_job_no_requirements(cli_client, archived_project_no_requirements):
    # Creating a job using CLI client
    args = {
        'name': 'published_job_no_requirements',
        'entrypoint': DEFAULT_ENTRYPOINT,
        'requirements': DEFAULT_REQUIREMENTS
    }
    rv = cli_client.put('/api/v1/publish',
                        query_string=args,
                        data={'seamless_project': (archived_project_no_requirements, "prj.tar.gz")},
                        content_type="multipart/form-data")

    yield rv.json['job_id']

    # Deleting the job using CLI client
    cli_client.delete(f'/api/v1/jobs/published_job_no_requirements')


@pytest.fixture
def archived_project_default_requirements():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    folder_to_archive = os.path.join(dir_path, '..', 'test_project_default_requirements')

    handler = io.BytesIO()
    with tarfile.open(fileobj=handler, mode="w:gz") as tar:
        tar.add(folder_to_archive, arcname='.')
        tar.close()

    handler.seek(0)  # going back to the start after writing into it
    return handler


@pytest.fixture
def published_job_default_requirements(cli_client, archived_project_default_requirements):
    # Creating a job using CLI client
    args = {
        'name': 'published_job_default_requirements',
        'entrypoint': DEFAULT_ENTRYPOINT,
        'requirements': DEFAULT_REQUIREMENTS
    }
    rv = cli_client.put('/api/v1/publish',
                        query_string=args,
                        data={'seamless_project': (archived_project_default_requirements, "prj.tar.gz")},
                        content_type="multipart/form-data")

    yield rv.json['job_id']

    # Deleting the job using CLI client
    cli_client.delete(f'/api/v1/jobs/published_job_default_requirements')


@pytest.fixture
def archived_project_custom_requirements_custom_entrypoint():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    folder_to_archive = os.path.join(dir_path, '..', 'test_project_custom_requirements_custom_entrypoint')

    handler = io.BytesIO()
    with tarfile.open(fileobj=handler, mode="w:gz") as tar:
        tar.add(folder_to_archive, arcname='.')
        tar.close()

    handler.seek(0)  # going back to the start after writing into it
    return handler


@pytest.fixture
def published_job_custom_requirements_custom_entrypoint(cli_client,
                                                        archived_project_custom_requirements_custom_entrypoint):
    # Creating a job using CLI client
    args = {
        'name': 'published_job_custom_requirements_custom_entrypoint',
        'entrypoint': 'custom_function.py',
        'requirements': 'custom_requirements.txt'
    }
    rv = cli_client.put('/api/v1/publish',
                        query_string=args,
                        data={'seamless_project': (archived_project_custom_requirements_custom_entrypoint, "prj.tar.gz")},
                        content_type="multipart/form-data")

    yield rv.json['job_id']

    # Deleting the job using CLI client
    cli_client.delete(f'/api/v1/jobs/published_job_custom_requirements_custom_entrypoint')
