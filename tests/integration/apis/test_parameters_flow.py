import io
import os
import tarfile
from time import sleep

import pytest

from constants import DEFAULT_ENTRYPOINT
from core.models import get_db_session, JobRun


@pytest.fixture
def job_with_parameters_name():
    return 'Integration test job with parameters name'


@pytest.fixture
def archived_project_with_parameters():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    folder_to_archive = os.path.join(dir_path, '../..', 'test_project_with_parameters')

    handler = io.BytesIO()
    with tarfile.open(fileobj=handler, mode="w:gz") as tar:
        tar.add(folder_to_archive, arcname='.')
        tar.close()

    handler.seek(0)  # going back to the start after writing into it
    return handler


@pytest.fixture
def published_job_with_parameters(cli_client,
                                  job_with_parameters_name,
                                  archived_project_with_parameters):
    # Creating a job using CLI client
    args = {
        'name': job_with_parameters_name,
        'entrypoint': DEFAULT_ENTRYPOINT
    }
    rv = cli_client.put('/api/v1/publish',
                        query_string=args,
                        data={'seamless_project': (archived_project_with_parameters, "prj.tar.gz")},
                        content_type="multipart/form-data")

    yield rv.json['job_id']

    # Deleting the job using CLI client
    cli_client.delete(f'/api/v1/jobs/{job_with_parameters_name}')


def test_non_existing_job_parameters(web_client):
    rv = web_client.get('/api/v1/jobs/234234/parameters')
    assert rv.status_code == 404

    # Payload does not matter because the Job does not exist
    rv = web_client.post('/api/v1/jobs/234234/parameters', json={"key": "key", "value": "value"})
    assert rv.status_code == 404

    rv = web_client.delete('/api/v1/jobs/234234/parameters/234234')
    assert rv.status_code == 404


@pytest.mark.skip(reason="requirements.txt has a known bug")
def test_parameters_flow(web_client, published_job_with_parameters):
    test_parameter_1 = {"key": "key1", "value": "value1"}
    test_parameter_2 = {"key": "key2", "value": "value2"}

    rv = web_client.get(f'/api/v1/jobs/{published_job_with_parameters}/parameters')
    assert rv.status_code == 200
    assert len(rv.json) == 0  # There are no parameters attached to this job yet

    rv = web_client.post(f'/api/v1/jobs/{published_job_with_parameters}/parameters', json=test_parameter_1)
    assert rv.status_code == 200  # We've added one parameter

    rv = web_client.get(f'/api/v1/jobs/{published_job_with_parameters}/parameters')
    assert rv.status_code == 200
    assert len(rv.json) == 1  # There is one parameter that we've added
    parameter = rv.json[0]
    assert parameter['key'] == test_parameter_1['key']
    assert parameter['value'] == test_parameter_1['value']

    rv = web_client.post(f'/api/v1/jobs/{published_job_with_parameters}/parameters', json=test_parameter_2)
    assert rv.status_code == 200  # We've added a second parameter

    rv = web_client.get(f'/api/v1/jobs/{published_job_with_parameters}/parameters')
    assert rv.status_code == 200
    assert len(rv.json) == 2  # There are two parameters that we've added
    parameter_1 = rv.json[0]
    parameter_2 = rv.json[1]
    assert parameter_1['key'] == test_parameter_1['key']
    assert parameter_1['value'] == test_parameter_1['value']
    assert parameter_2['key'] == test_parameter_2['key']
    assert parameter_2['value'] == test_parameter_2['value']

    rv = web_client.delete(f'/api/v1/jobs/{published_job_with_parameters}/parameters/{parameter_2["id"]}')
    assert rv.status_code == 200  # We've just deleted a second parameter

    rv = web_client.get(f'/api/v1/jobs/{published_job_with_parameters}/parameters')
    assert rv.status_code == 200
    assert len(rv.json) == 1  # We're back to the one parameter we added first
    parameter = rv.json[0]
    assert parameter['key'] == test_parameter_1['key']
    assert parameter['value'] == test_parameter_1['value']

    rv = web_client.post(f'/api/v1/jobs/{published_job_with_parameters}/run')
    assert rv.status_code == 200  # We've just triggered a Job run

    job_run = get_db_session().query(JobRun).filter(JobRun.job_id == published_job_with_parameters).one()
    logs = []
    for i in range(5):
        sleep(1)
        logs = list(job_run.logs)
        if len(logs) == 1:  # We are waiting for a single logs line to appear
            break
    if len(logs) == 0:
        assert False, "Running the job with parameters did not produce logs in the database"
    else:
        assert len(logs) == 1
        assert test_parameter_1['value'] in logs[0].message  # Logs have the value of a parameter
