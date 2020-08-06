import os
from unittest import mock

import pytest

from backend.db import get_session
from backend.db.models.jobs import Job
from backend.db.models.job_runs import JobRunType


def path_to_project():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, '..', 'test_project/')


@mock.patch('backend.db.models.job_runs.send_update')
@mock.patch('backend.db.models.job_run_logs.send_update')
@mock.patch('backend.db.models.job_runs.project.get_path_to_job', return_value=path_to_project())
def test_execution_flow(*args):

    # add job arhive somewhere
    session = get_session()
    job = Job(user_id=1, name='another_test_name_17', entrypoint='main_module.read_news', requirements='custom_requirements.txt')
    session.add(job)
    session.commit()

    job.execute(JobRunType.RunButton.value)

    session.commit()
