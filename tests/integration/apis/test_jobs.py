import base64

import config


def _basic_auth_headers():
    username = config.LAMBDA_PROXY_AUTH_USERNAME
    password = config.LAMBDA_PROXY_PASSWORD
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(bytes(f"{username}:{password}", 'utf-8')).decode('utf-8')
    }
    return headers


def test_job_by_schedule_auth(automation_client):
    payload = {'job_id': '234234'}  # non-existent job, we are testing auth here
    rv = automation_client.post('/api/v1/jobs/execute', json=payload)
    assert rv.status_code == 401, "We are not authorized now"

    rv = automation_client.post('/api/v1/jobs/execute', json=payload, headers=_basic_auth_headers())
    assert rv.status_code == 404, "We should receive 404, since we are authorized, but job does not exist"
