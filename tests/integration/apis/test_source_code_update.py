from constants import DEFAULT_ENTRYPOINT
from core.models import get_db_session
from core.models.job_runs import JobRun, JobRunType
from core.services import job as job_service

PRINT_MSG = "Hello there. I'm a new code and I'm alive."

NEW_CODE_CONTENTS = f"""
def main():
    print("{PRINT_MSG}")


if __name__ == '__main__':
    main()
"""


def test_code_update(web_client, published_job_default_requirements, user_id):
    job_id = published_job_default_requirements

    res = web_client.put(f'/api/v1/jobs/{job_id}/source-code', json={
        'filename': DEFAULT_ENTRYPOINT,
        'contents': NEW_CODE_CONTENTS
    })
    assert res.status_code == 200

    job_service.execute(job_id, JobRunType.RunButton.value, user_id)

    session = get_db_session()
    job_run = session.query(JobRun).filter_by(job_id=job_id).one()
    logs = [log.message for log in job_run.logs]

    assert f"{PRINT_MSG}\n" in logs, "There should be custom message provided in the test"
