import base64
import os

import constants
from core.models import get_db_session, JobTemplate
from core.services.marketplace import fetch_template_from_s3


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

    file_on_s3 = fetch_template_from_s3(str(template.id))
    assert file_on_s3.getbuffer().nbytes > 0  # There is a real archived that was saved to s3
    # TODO assert that the file actually corresponds to files of the template

    resp = web_client.get('/api/v1/templates')
    assert resp.status_code == 200
    assert len(resp.json) == 1  # There is one template that we've just uploaded
    template_from_json = resp.json[0]
    assert template_from_json['name'] == 'template1'
    assert template_from_json['short_description'] == 'template1'
    assert template_from_json['long_description_url'] == 'template1'
    assert template_from_json['tags'] == 'template1'
