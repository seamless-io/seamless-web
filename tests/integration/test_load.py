import tarfile
from collections import defaultdict
from time import sleep

import requests

from core.db import session_scope
from core.db.models import Job
from core.db.models.job_runs import JobRunResult
from core.helpers import row2dict
from tests.integration.test_seamless_project.function import pi, PI_DIGITS

PUBLISH_URL = f"https://staging-app.seamlesscloud.io/api/v1/publish"
DELETE_URL = f"https://staging-app.seamlesscloud.io/api/v1/jobs/"
PACKAGE_NAME = "seamless_package.tar.gz"
TEST_SCHEDULE = "* * * * *"
TEST_RUNS = 3
JOBS_PER_USER = 2

# Add a 2-minute buffer so we don't miss executions
# It could take up to 1 minutes from the job publishing to first event
WAIT_FOR_EXECUTION_SECONDS = 60 * (TEST_RUNS + 2)

# Seems like a limitation of postgres, but I'm not sure
MAX_LOGS_ROW_LENGTH = 16384


def test_load(test_users):

    # We should be able to find this value in logs later
    pi_digits = str(pi())

    # Create test jobs using the API
    tar = tarfile.open(PACKAGE_NAME, "w:gz")
    tar.add("tests/integration/test_seamless_project", ".")
    tar.close()
    created_job_ids_by_user_id = defaultdict(list)
    created_job_names_by_user_id = defaultdict(list)
    for user in test_users:
        for i in range(JOBS_PER_USER):
            job_name = f"user_{user['id']}_job_{i}"
            resp = requests.put(PUBLISH_URL,
                                params={"name": job_name,
                                        "schedule": TEST_SCHEDULE},
                                headers={'Authorization': user['api_key']},
                                files={'seamless_project': open(PACKAGE_NAME, 'rb')})
            resp.raise_for_status()
            created_job_ids_by_user_id[user['id']].append(resp.json()['job_id'])
            created_job_names_by_user_id[user['id']].append(job_name)

    # Wait until they are all executed
    sleep(WAIT_FOR_EXECUTION_SECONDS)

    try:
        with session_scope() as db_session:
            for user in test_users:
                for job_id in created_job_ids_by_user_id[user['id']]:
                    job = db_session.query(Job).get(job_id)

                    # There may be more runs because of the buffer, but we only check first TEST_RUNS
                    job_runs = sorted(list(job.runs), key=lambda x: x.created_at)[:TEST_RUNS]
                    print([row2dict(l) for l in job_runs])

                    # Each job should be executed at least TEST_RUNS times
                    # But no more than TEST_RUNS + 1 because of WAIT_FOR_EXECUTION_SECONDS
                    assert TEST_RUNS <= len(job_runs) <= TEST_RUNS + 2

                    # Make sure runs are 1 minute +/- 5 seconds from each other
                    timestamps = [r.created_at for r in job_runs]
                    for i in range(len(timestamps) - 1):
                        assert abs((timestamps[i + 1] - timestamps[i]).total_seconds() - 60) < 5

                    for run in job_runs:
                        logs = list(run.logs)
                        print([row2dict(l) for l in logs])

                        # All executions should be successful
                        assert run.status == JobRunResult.Ok.value

                        # Logs recorded for each job should be exactly like this
                        assert logs[0].message == 'SciPy version: 1.5.1\n'
                        assert logs[1].message == 'Executing...\n'
                        index = 2
                        for i in range(0, PI_DIGITS, MAX_LOGS_ROW_LENGTH):
                            if i + MAX_LOGS_ROW_LENGTH < len(pi_digits):
                                pi_digits_in_logs = pi_digits[i: i + MAX_LOGS_ROW_LENGTH]
                            else:
                                pi_digits_in_logs = f'{pi_digits[i:]}\n'
                            assert logs[index].message == pi_digits_in_logs
                            index += 1
    finally:
        # Remove all test jobs using the API
        for user in test_users:
            for job_name in created_job_names_by_user_id[user['id']]:
                resp = requests.delete(f"{DELETE_URL}{job_name}",
                                       headers={'Authorization': user['api_key']})
                resp.raise_for_status()
