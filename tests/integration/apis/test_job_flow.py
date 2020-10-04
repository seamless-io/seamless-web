import pytest

import core.services.job as job_service


def test_vanilla(web_client):
    res = web_client.get('/', follow_redirects=True)
    assert res.status_code == 200


def test_publish_user_not_found(cli_client):
    rv = cli_client.put('/api/v1/publish', headers={'Authorization': 'some_good_key'})
    assert b'API Key is wrong' in rv.data
    assert rv.status_code == 400


def test_publish_file_not_provided(cli_client):
    rv = cli_client.put('/api/v1/publish')
    assert b'File not provided' in rv.data
    assert rv.status_code == 400


def test_publish_and_delete_from_web(cli_client, web_client, user_id, job_name, job_entrypoint, job_requirements,
                                     archived_project):
    args = {
        'name': job_name,
        'entrypoint': job_entrypoint,
        'requirements': job_requirements
    }
    rv = cli_client.put('/api/v1/publish',
                        query_string=args,
                        data={'seamless_project': (archived_project, "prj.tar.gz")},
                        content_type="multipart/form-data")
    assert rv.status_code == 200

    job = job_service.get_job_by_name(job_name, user_id)  # Make sure job is stored in the database

    # Please note we're testing the delete method for the WEB UI
    web_client.delete(f'/api/v1/jobs/{str(job.id)}/delete')
    with pytest.raises(job_service.JobNotFoundException):
        job_service.get_job_by_name(job_name, user_id)  # The job is no longer in the database


def test_publish_and_delete_from_cli(cli_client, user_id, job_name, job_entrypoint, job_requirements, archived_project):
    args = {
        'name': job_name,
        'entrypoint': job_entrypoint,
        'requirements': job_requirements
    }
    rv = cli_client.put('/api/v1/publish',
                        query_string=args,
                        data={'seamless_project': (archived_project, "prj.tar.gz")},
                        content_type="multipart/form-data")
    assert rv.status_code == 200

    job = job_service.get_job_by_name(job_name, user_id)  # Make sure job is stored in the database

    # Please note we're testing the delete method for the CLI
    cli_client.delete(f'/api/v1/jobs/{job_name}')
    with pytest.raises(job_service.JobNotFoundException):
        job_service.get_job_by_name(job_name, user_id)  # The job is no longer in the database


def test_publish_and_update_schedule(cli_client, web_client, user_id, job_name, job_entrypoint, job_requirements,
                                     archived_project):
    args = {
        'name': job_name,
        'entrypoint': job_entrypoint,
        'requirements': job_requirements
    }
    rv = cli_client.put('/api/v1/publish',
                        query_string=args,
                        data={'seamless_project': (archived_project, "prj.tar.gz")},
                        content_type="multipart/form-data")
    assert rv.status_code == 200
    job = job_service.get_job_by_name(job_name, user_id)
    assert job.cron is None
    assert job.aws_cron is None
    assert job.human_cron is None
    assert job.schedule_is_active is None

    resp = web_client.put(f'/api/v1/jobs/{str(job.id)}/schedule',
                          query_string={'cron': 'wrong_cron',
                                        'is_enabled': 'true'})
    assert resp.status_code == 400
    job = job_service.get_job_by_name(job_name, user_id)
    assert job.cron is None
    assert job.aws_cron is None
    assert job.human_cron is None
    assert job.schedule_is_active is None

    resp = web_client.put(f'/api/v1/jobs/{str(job.id)}/schedule',
                          query_string={'cron': '* * * * *',
                                        'is_enabled': 'true'})
    assert resp.status_code == 200

    job = job_service.get_job_by_name(job_name, user_id)
    assert job.cron == '* * * * *'
    assert job.aws_cron == '* * * * ? *'
    assert job.human_cron == 'Every minute'
    assert job.schedule_is_active is True

    resp = web_client.put(f'/api/v1/jobs/{str(job.id)}/schedule',
                          query_string={'is_enabled': 'false'})
    assert resp.status_code == 200

    job = job_service.get_job_by_name(job_name, user_id)
    assert job.cron == '* * * * *'
    assert job.aws_cron == '* * * * ? *'
    assert job.human_cron == 'Every minute'
    assert job.schedule_is_active is False
