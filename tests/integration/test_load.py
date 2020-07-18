import tarfile

import requests

from tests.integration.conftest import JOBS_PER_USER

PUBLISH_URL = f"https://staging-app.seamlesscloud.io/api/v1/publish"
PACKAGE_NAME = "seamless_package.tar.gz"


def test_load(test_users):
    tar = tarfile.open(PACKAGE_NAME, "w:gz")
    tar.add("tests/integration/test_seamless_project")
    tar.close()
    for user in test_users:
        for i in range(JOBS_PER_USER):
            resp = requests.put(PUBLISH_URL,
                                params={"name": f"user_{user['id']}_job_{i}"},
                                headers={'Authorization': user['api_key']},
                                files={'seamless_project': open(PACKAGE_NAME, 'rb')})
            resp.raise_for_status()
