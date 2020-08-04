import pytest

from job_executor import executor
from job_executor.exceptions import ExecutorBuildException, ExecutorRuntimeException


@pytest.fixture
def path_to_project():
    return 'tests/test_project/main_module.py'

@pytest.fixture
def path_to_requirements():
    return 'tests/test_project/custom_requirements.txt'

@pytest.fixture
def entrypoint():
    return 'main_module.read_news'

def test_execute_succesfull(path_to_project, path_to_requirements, entrypoint):
    # we are reading from https://en.wikipedia.org/wiki/List_of_news_media_APIs
    output = list(executor.execute(path_to_project, entrypoint, path_to_requirements))
    assert "List of news media APIs" in output
    assert "Everything is alright" in output  # return value from the function in `test_project.main_module.read_news`


def test_execute_wrong_entrypoint(path_to_project, path_to_requirements):
    wrong_entrypoint = 'wrong_entrypoint'
    # TODO: add suggestions later:
    # * "... did you provide dot-separated path to the function correctly?
    # * Maybe you meant: function.main"
    # if `.py` in entrypoint: "do not need to put file extensions in entrypoint"
    with pytest.raises(ExecutorRuntimeException, match=f"Cannot find function to execute `{wrong_entrypoint}`*"):
        output = list(executor.execute(path_to_project, wrong_entrypoint, path_to_requirements))


def test_execute_wrong_requirements(path_to_project, entrypoint):
    wrong_requirements_path = 'requirements_wrong.txt'
    with pytest.raises(ExecutorBuildException, match=f"Cannot find requirements file `{wrong_requirements_path}`*"):
        output = list(executor.execute(path_to_project, entrypoint, wrong_requirements_path))


def test_execute_wrong_project_path(entrypoint, path_to_requirements):
    wrong_project_path = '/usr/local/bin'
    with pytest.raises(ExecutorBuildException):
        output = list(executor.execute(wrong_project_path, entrypoint, path_to_requirements))

