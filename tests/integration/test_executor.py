import os
import re

import pytest

from job_executor import executor
from job_executor.exceptions import ExecutorBuildException


@pytest.fixture
def path_to_project():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, '..', 'test_project/')


@pytest.fixture
def path_to_requirements():
    return 'custom_requirements.txt'


@pytest.fixture
def entrypoint():
    return 'function.py'


@pytest.fixture
def entrypoint_to_corrupted_program():
    return 'main_exception.py'


def test_execute_succesfull(path_to_project, path_to_requirements, entrypoint):
    # we are reading from https://en.wikipedia.org/wiki/List_of_news_media_APIs
    parameters = {}
    with executor.execute(path_to_project, entrypoint, parameters, path_to_requirements) as res:
        assert "List of news media APIs" in ''.join(list(res.output))
        assert res.get_exit_code() == 0


@pytest.mark.skip(reason="We do not handle return values yet")
def test_execute_succesfull_return_value(path_to_project, path_to_requirements, entrypoint):
    # we are reading from https://en.wikipedia.org/wiki/List_of_news_media_APIs
    parameters = {}
    with executor.execute(path_to_project, entrypoint, parameters, path_to_requirements) as res:
        return_value_from_function = "Everything is alright"
        assert return_value_from_function in ''.join(res.output)


def test_execute_wrong_entrypoint_file(path_to_project, path_to_requirements):
    wrong_entrypoint_filename = 'wrong_entrypoint.smls'
    # # TODO: add suggestions later:
    # # * "... did you provide a path to the file correctly?
    # # * Maybe you meant: function.py"
    parameters = {}
    exc_msg = re.escape(f"{ExecutorBuildException.PREFIX} Path to entrypoint file is not valid: "
                        f"`{wrong_entrypoint_filename}`")
    with pytest.raises(ExecutorBuildException, match=exc_msg):
        with executor.execute(path_to_project, wrong_entrypoint_filename, parameters, path_to_requirements) as res:
            print(f"ok {res}")


def test_execute_wrong_requirements(path_to_project, entrypoint):
    wrong_requirements_path = 'requirements_wrong.txt'
    exc_msg = re.escape(f"{ExecutorBuildException.PREFIX} Cannot find requirements file `{wrong_requirements_path}`")
    parameters = {}
    with pytest.raises(ExecutorBuildException, match=exc_msg):
        with executor.execute(path_to_project, entrypoint, parameters, wrong_requirements_path) as res:
            print(f"ok {res}")


def test_execute_wrong_project_path(entrypoint, path_to_requirements):
    wrong_project_path = '/this/is/non/existing/path'
    exc_msg = re.escape(f"{ExecutorBuildException.PREFIX} Invalid project path directory `{wrong_project_path}` does not exist")
    with pytest.raises(ExecutorBuildException, match=exc_msg):
        with executor.execute(wrong_project_path, entrypoint, path_to_requirements) as res:
            print(f"ok {res}")


def test_execute_project_with_error(path_to_project, entrypoint_to_corrupted_program, path_to_requirements):
    parameters = {}
    with executor.execute(path_to_project, entrypoint_to_corrupted_program, parameters, path_to_requirements) as res:
        assert "Traceback" in ''.join(res.output)
        assert res.get_exit_code() == 1


def test_legacy_entrypoint(path_to_project, path_to_requirements):
    legacy_entrypoint = 'function.main'
    parameters = {}
    with executor.execute(path_to_project, legacy_entrypoint, parameters, path_to_requirements) as res:
        assert "List of news media APIs" in ''.join(list(res.output))
        assert res.get_exit_code() == 0
