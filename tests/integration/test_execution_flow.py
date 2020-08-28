import os
from unittest import mock

from core.services import job as job_service
from core.models.jobs import Job
from core.models.job_runs import JobRun, JobRunType


def path_to_project():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, '..', 'test_project/')


@mock.patch('core.services.job.send_update')
@mock.patch('core.services.job.project.get_path_to_job', return_value=path_to_project())
def test_execution_flow(get_path, send_update, session_id):
    pass  # TODO make it work
    # job_runs_count_initial = get_db_session().query(JobRun).count()
    #
    # # create job we want to execute later
    # job = Job(user_id=1, name=f'another_test_name_{session_id}',
    #           entrypoint='main_module.read_news', requirements='custom_requirements.txt')
    # get_db_session().add(job)
    # db_commit()
    #
    # job_service.execute(job.id, JobRunType.RunButton.value, '1')
    #
    # assert send_update.called
    #
    # job_runs_count_new = session.query(JobRun).count()
    # assert job_runs_count_initial + 1 == job_runs_count_new, "New JobRun should be created"
