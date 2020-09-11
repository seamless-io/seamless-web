from time import sleep

from core.models import get_db_session, JobRun


def _run_job_and_assert_logs(web_client, job_id, string_to_find_in_logs):
    rv = web_client.post(f'/api/v1/jobs/{job_id}/run')
    assert rv.status_code == 200  # We've just triggered a Job run

    job_run = get_db_session().query(JobRun).filter(JobRun.job_id == job_id).one()
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
        assert string_to_find_in_logs in logs[0].message


def test_job_run_no_requirements_no_parameters(web_client, published_job_no_requirements):
    _run_job_and_assert_logs(web_client, published_job_no_requirements, 'TEST OUTPUT: None')


def test_job_run_no_requirements_with_parameters(web_client, published_job_no_requirements):
    test_parameter = {"key": "key1", "value": "value1"}
    rv = web_client.post(f'/api/v1/jobs/{published_job_no_requirements}/parameters',
                         json=test_parameter)
    assert rv.status_code == 200  # We've added one parameter

    _run_job_and_assert_logs(web_client, published_job_no_requirements, 'TEST OUTPUT: value1')


def test_job_run_default_requirements_no_parameters(web_client, published_job_default_requirements):
    _run_job_and_assert_logs(web_client, published_job_default_requirements,
                             'TEST OUTPUT: None; requests_version: 2.19.0')


def test_job_run_default_requirements_with_parameters(web_client, published_job_default_requirements):
    test_parameter = {"key": "key1", "value": "value1"}
    rv = web_client.post(f'/api/v1/jobs/{published_job_default_requirements}/parameters',
                         json=test_parameter)
    assert rv.status_code == 200  # We've added one parameter

    _run_job_and_assert_logs(web_client, published_job_default_requirements,
                             'TEST OUTPUT: value1; requests_version: 2.19.0')


def test_job_run_custom_requirements_custom_entrypoint_no_parameters(
        web_client, published_job_custom_requirements_custom_entrypoint):
    _run_job_and_assert_logs(web_client, published_job_custom_requirements_custom_entrypoint,
                             'TEST OUTPUT: None; requests_version: 2.19.0')


def test_job_run_custom_requirements_custom_entrypoint_with_parameters(
        web_client, published_job_custom_requirements_custom_entrypoint):
    test_parameter = {"key": "key1", "value": "value1"}
    rv = web_client.post(f'/api/v1/jobs/{published_job_custom_requirements_custom_entrypoint}/parameters',
                         json=test_parameter)
    assert rv.status_code == 200  # We've added one parameter

    _run_job_and_assert_logs(web_client, published_job_custom_requirements_custom_entrypoint,
                             'TEST OUTPUT: value1; requests_version: 2.19.0')
