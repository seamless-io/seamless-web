import pytest


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
