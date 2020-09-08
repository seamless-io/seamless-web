import base64
import os

import constants
from core.models import get_db_session, JobTemplate


def _basic_auth_headers():
    username = constants.GITHUB_ACTIONS_USERNAME
    password = os.getenv('GITHUB_ACTIONS_PASSWORD')
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(bytes(f"{username}:{password}", 'utf-8')).decode('utf-8')
    }
    return headers


def test_marketplace_update_flow(web_client, automation_client, archived_templates_repo):
    resp = web_client.get('/api/v1/templates')
    assert resp.status_code == 200
    assert len(resp.json) == 0  # There are no templates in the database yet

    resp = automation_client.post('/api/v1/marketplace')
    assert resp.status_code == 401  # We need to authenticate

    resp = automation_client.post('/api/v1/marketplace', headers=_basic_auth_headers())
    assert resp.status_code == 400  # We need to send a package with templates files

    resp = automation_client.post('/api/v1/marketplace', headers=_basic_auth_headers(),
                                  data={'templates': open(archived_templates_repo, 'rb')})
    assert resp.status_code == 200  # Good, now let's make sure the data is in database

    templates_in_db = get_db_session().query(JobTemplate).all()
    assert len(templates_in_db) == 1  # We have only 1 template
    template = templates_in_db[0]
    # Data in db has to match the data in the marketplace_templates_files/table_of_contents.yml file
    assert template.name == 'template1'
    assert template.short_description == 'template1'
    assert template.long_description_url == 'template1'
    assert template.tags == 'template1'
