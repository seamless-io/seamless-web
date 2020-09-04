from base64 import b64encode

import pytest
from requests.auth import _basic_auth_str

import config


@pytest.mark.usefixtures('postgres')
def test_marketplace_update_flow(flask_test_client):
    resp = flask_test_client.get('/api/v1/templates')
    assert resp.status_code == 200
    assert len(resp.json) == 0  # There are no templates in the database yet

    print(config.GITHUB_ACTIONS_USER, config.GITHUB_ACTIONS_PASSWORD)
    print('OLOLOLOL')
    resp = flask_test_client.post('/api/v1/marketplace')
    assert resp.status_code == 401  # We need to authenticate

    # credentials = b64encode(f"{GITHUB_ACTIONS_USER}:{GITHUB_ACTIONS_PASSWORD}".encode())
    resp = flask_test_client.post('/api/v1/marketplace',
                                  headers={"Authorization": _basic_auth_str(GITHUB_ACTIONS_USER,
                                                                            GITHUB_ACTIONS_PASSWORD)})
    assert resp.status_code == 200
