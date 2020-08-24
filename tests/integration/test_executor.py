import os
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
    return 'main_module.py'

@pytest.fixture
def entrypoint_to_corrupted_program():
    return 'main_exception.py'


def test_execute_succesfull(path_to_project, path_to_requirements, entrypoint):
    # we are reading from https://en.wikipedia.org/wiki/List_of_news_media_APIs
    res = executor.execute(path_to_project, entrypoint, path_to_requirements)
    assert "List of news media APIs" in ''.join(list(res.output))
    assert res.exit_code == 0


@pytest.mark.skip(reason="We do not handle return values yet")
def test_execute_succesfull_return_value(path_to_project, path_to_requirements, entrypoint):
    # we are reading from https://en.wikipedia.org/wiki/List_of_news_media_APIs
    res = executor.execute(path_to_project, entrypoint, path_to_requirements)
    return_value_from_function = "Everything is alright"
    assert return_value_from_function in ''.join(res.output)


def test_execute_wrong_entrypoint_file(path_to_project, path_to_requirements):
    wrong_entrypoint_filename = 'wrong_entrypoint.smls'
    # # TODO: add suggestions later:
    # # * "... did you provide dot-separated path to the function correctly?
    # # * Maybe you meant: function.main"
    # # if `.py` in entrypoint: "do not need to put file extensions in entrypoint"
    with pytest.raises(ExecutorBuildException, match=f"Path to entrypoint file is not valid: `{wrong_entrypoint_filename}`*"):
        executor.execute(path_to_project, wrong_entrypoint_filename, path_to_requirements)


def test_execute_wrong_requirements(path_to_project, entrypoint):
    wrong_requirements_path = 'requirements_wrong.txt'
    with pytest.raises(ExecutorBuildException, match=f"Cannot find requirements file `{wrong_requirements_path}`*"):
        executor.execute(path_to_project, entrypoint, wrong_requirements_path)


def test_execute_wrong_project_path(entrypoint, path_to_requirements):
    wrong_project_path = '/this/is/non/existing/path'
    with pytest.raises(ExecutorBuildException, match=f"Invalid project path, "
                                                     f"directory `{wrong_project_path}` does not exist*"):
        executor.execute(wrong_project_path, entrypoint, path_to_requirements)


def test_execute_project_with_error(path_to_project, entrypoint_to_corrupted_program, path_to_requirements):
    res = executor.execute(path_to_project, entrypoint_to_corrupted_program, path_to_requirements)
    assert "Traceback" in ''.join(res.output)
    assert res.exit_code == 1
