import tarfile
from collections import defaultdict
from time import sleep

import requests

from backend.db import session_scope
from backend.db.models import Job
from backend.db.models.job_runs import JobRunResult
from backend.helpers import row2dict
from job_executor.scheduler import remove_job_schedule
from tests.integration.conftest import JOBS_PER_USER

PUBLISH_URL = f"https://staging-app.seamlesscloud.io/api/v1/publish"
DELETE_URL = f"https://staging-app.seamlesscloud.io/api/v1/jobs/"
PACKAGE_NAME = "seamless_package.tar.gz"
TEST_SCHEDULE = "* * * * *"
TEST_RUNS = 5
WAIT_FOR_EXECUTION_SECONDS = 60 * (TEST_RUNS + 1)  # Add a buffer so we don't miss executions


def test_load(test_users):

    # Create test jobs using the API
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

    # Wait until they are all executed
    sleep(WAIT_FOR_EXECUTION_SECONDS)

    try:
        with session_scope() as db_session:
            for user in test_users:
                for job_id in created_job_ids_by_user_id[user['id']]:
                    job = db_session.query(Job).get(job_id)
                    job_runs = list(job.runs)
                    print([row2dict(l) for l in job_runs])

                    # Each job should be executed at least TEST_RUNS times
                    # But no more than TEST_RUNS + 1 because of WAIT_FOR_EXECUTION_SECONDS
                    assert TEST_RUNS <= len(job_runs) <= TEST_RUNS + 1

                    # There may be more runs because of the buffer, but we only check TEST_RUNS
                    for run in job_runs[:TEST_RUNS]:
                        logs = list(run.logs)
                        print([row2dict(l) for l in logs])

                        # All executions should be successful
                        assert run.status == JobRunResult.Ok.value

                        # Logs recorded for each job should be exactly like this
                        assert logs[0].message == 'SciPy version: 1.5.1\n'
                        assert logs[1].message == 'Executing...\n'
                        assert logs[2].message == 'Finished\n'
    finally:
        # Remove all test jobs using the API
        for user in test_users:
            for job_id in created_job_ids_by_user_id[user['id']]:
                resp = requests.delete(f"{DELETE_URL}{job_id}",
                                       headers={'Authorization': user['api_key']})
                resp.raise_for_status()

    # for i in range(327, 347):
    #     remove_job_schedule(str(i))
