import tarfile
from collections import defaultdict
from time import sleep

import requests

from tests.integration.conftest import JOBS_PER_USER

PUBLISH_URL = f"https://staging-app.seamlesscloud.io/api/v1/publish"
DELETE_URL = f"https://staging-app.seamlesscloud.io/api/v1/jobs/"
PACKAGE_NAME = "seamless_package.tar.gz"
TEST_SCHEDULE = "* * * * *"
TEST_RUNS = 1
WAIT_FOR_EXECUTION_SECONDS = 60 * (TEST_RUNS + 1)  # Add a buffer so we don't miss executions


def test_load(test_users):
    tar = tarfile.open(PACKAGE_NAME, "w:gz")
    tar.add("tests/integration/test_seamless_project", ".")
    tar.close()
    created_job_ids_by_user_id = defaultdict(list)
    for user in test_users:
        for i in range(JOBS_PER_USER):
            resp = requests.put(PUBLISH_URL,
                                params={"name": f"user_{user['id']}_job_{i}",
                                        "schedule": TEST_SCHEDULE},
                                headers={'Authorization': user['api_key']},
                                files={'seamless_project': open(PACKAGE_NAME, 'rb')})
            resp.raise_for_status()
            created_job_ids_by_user_id[user['id']].append(resp.json()['job_id'])

    sleep(WAIT_FOR_EXECUTION_SECONDS)

    for user in test_users:
        created_job_ids = created_job_ids_by_user_id[user['id']]
        for job_id in created_job_ids:
            resp = requests.delete(f"{DELETE_URL}{job_id}",
                                   headers={'Authorization': user['api_key']})
            resp.raise_for_status()
