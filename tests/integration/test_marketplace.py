import pytest


@pytest.mark.usefixtures('postgres')
def test_marketplace_update_flow(flask_test_client):
    resp = flask_test_client.get('/api/v1/templates')
    assert resp.status_code == 200
    assert len(resp.json) == 0  # There are no templates in the database yet
