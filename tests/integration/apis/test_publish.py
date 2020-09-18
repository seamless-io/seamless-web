from core.models import User, get_db_session


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


def test_publish_personal_workspace(cli_client, job_name, job_entrypoint, job_requirements, archived_project, user_id):
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

    user = User.get_user_from_id(user_id, get_db_session())
    personal_workspace = user.owned_workspaces[0]
    jobs = list(user.jobs)
    assert len(jobs) == 1  # We've just published a single job
    job = jobs[0]
    assert job.workspace_id == personal_workspace.id  # It was published to personal workspace by default
    assert len(list(personal_workspace.jobs)) == 1  # Our workspace has only a single job


def test_publish_non_personal_workspace():
    """
    Now we need to ensure that the user publishes his job to the right workspace
    when the user has more than a single Personal workspace
    """
    pass
