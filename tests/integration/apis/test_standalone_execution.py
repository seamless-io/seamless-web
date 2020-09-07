import requests


def test_auth_error():
    rv = requests.post('/api/v1/run')
    assert rv.status_code == 401


def test_execute_standalone_project(cli_client, job_entrypoint, job_requirements, archived_project):
    args = {
        'entrypoint': job_entrypoint,
        'requirements': job_requirements
    }
    rv = cli_client.post('/api/v1/run',
                         query_string=args,
                         data={'seamless_project': (archived_project, "prj.tar.gz")},
                         content_type="multipart/form-data")
    assert rv.status_code == 200
    assert "American Broadcasting Company" in ''.join([str(line) for line in rv.iter_encoded()])
