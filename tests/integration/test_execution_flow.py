import os
from unittest import mock

import pytest

from core.models import get_session
from core.models.jobs import Job
from core.models.job_runs import JobRun, JobRunType


def path_to_project():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, '..', 'test_project/')


@mock.patch('core.models.job_runs.send_update')
@mock.patch('core.models.job_run_logs.send_update')
@mock.patch('core.models.job_runs.project.get_path_to_job', return_value=path_to_project())
def test_execution_flow(get_path, send_update_logs, send_update_status, session_id):
    session = get_session()

    job_runs_count_initial = session.query(JobRun).count()

    job = Job(user_id=1, name=f'another_test_name_{session_id}',
              entrypoint='main_module.read_news', requirements='custom_requirements.txt')
    session.add(job)
    session.commit()

    job.execute(JobRunType.RunButton.value)

    session.commit()

    assert send_update_logs.called, "Should've been called at least 1 time (one call per output line)"
    assert send_update_status.called
    assert send_update_status.call_count == 2  # to executing -> to succeed

    job_runs_count_new = session.query(JobRun).count()
    assert job_runs_count_initial + 1 == job_runs_count_new, "New JobRun should be created"
