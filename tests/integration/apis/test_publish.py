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


def test_publish_success(cli_client, job_name, job_entrypoint, job_requirements, archived_project):
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


def test_publish_to_the_team():
    """
    Now we need to ensure that the user publishes his job to the right workspace
    """
    pass
