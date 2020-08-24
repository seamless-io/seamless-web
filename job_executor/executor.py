# TODO: all errors from executor internal functionality should be caught and processed accordingly
# TODO: add periodic task to clean-up images: docker_client.images.prune(filters={'dangling': True})
import os
import contextlib
from dataclasses import dataclass
from typing import Optional, Generator, Any

import docker
from docker.models.containers import Container
from docker.types import Mount

from .exceptions import ExecutorBuildException

DOCKER_FILE_NAME = "Dockerfile"
REQUIREMENTS_FILENAME = "requirements.txt"
JOB_LOGS_RETENTION_DAYS = 1

@dataclass
class ExecuteResult:
    output: Generator[str, Any, None]
    exit_code: int


def execute(path_to_job_files: str,
            entrypoint_filename: str,
            path_to_requirements: Optional[str] = None) -> ExecuteResult:
    """
    Executing in docker container
    :param path_to_job_files: path to job files
    :param entrypoint: entrypoint provided by a user
    :param path_to_requirements: path to requirements provided by a user
    :return an instance of ExecuteResult
    """
    # TODO: make separation between requirements_absolute and relative
    check_project_path(path_to_job_files)
    check_entrypoint_file(path_to_job_files, entrypoint_filename)
    requirements_path = _ensure_requirements(path_to_job_files, path_to_requirements)
    with _run_container(path_to_job_files, entrypoint_filename, requirements_path) as container:
        return ExecuteResult(
            (str(log, 'utf-8') for log in container.logs(stream=True)),
            container.wait()['StatusCode']
        )

def check_entrypoint_file(job_directory: str, entrypoint_filename: str):
    # TODO: possibly check if the file has allowed extension `[.py, .rs, .java]`
    if not os.path.isfile(os.path.join(job_directory, entrypoint_filename)):
        raise ExecutorBuildException(f"Path to entrypoint file is not valid: `{entrypoint_filename}`")


def check_project_path(path_to_job_files):
    if not os.path.isdir(path_to_job_files):
        raise ExecutorBuildException(f"Invalid project path, directory `{path_to_job_files}` does not exist")


def _ensure_requirements(job_directory: str, requirements: Optional[str]):
    """
    Dockerfile execute `ADD` operations with requirements. So, we are ensuring that it exists
    """
    # path_to_requirements = f"{job_directory}/{requirements}"
    if requirements is None:
        # path was not provided by a user - create empty `requirements.txt`
        relative_requirements_path = 'requirements.txt'
        path_to_requirements = os.path.join(job_directory, 'requirements.txt')
        with open(path_to_requirements, 'w'):
            pass
    else:
        # path to requirements was provided by user. Check if exists
        path_to_requirements = os.path.join(job_directory, requirements)
        if not os.path.exists(path_to_requirements):
            raise ExecutorBuildException(f"Cannot find requirements file `{requirements}`")
        else:
            relative_requirements_path = requirements
    return relative_requirements_path


@contextlib.contextmanager
def _run_container(job_directory: str, entrypoint_filename: str, path_to_requirements: str) -> Container:
    dockerfile_contents = f"""
FROM python:3.8-slim
WORKDIR /src
ADD {path_to_requirements} /src/requirements.txt
RUN pip install -r requirements.txt
"""
    docker_client = docker.from_env()
    with open(os.path.join(job_directory, DOCKER_FILE_NAME), 'w') as dockerfile:
        dockerfile.write(dockerfile_contents)
    image, logs = docker_client.images.build(
        path=job_directory)

    try:
        container = docker_client.containers.run(
            image=image,
            command=f"bash -c \"python -u {entrypoint_filename}\"",
            mounts=[Mount(target='/src',
                          source=job_directory,
                          type='bind',
                          read_only=True)],
            auto_remove=False,
            detach=True,
            mem_limit='128m',
            memswap_limit='128m',
        )
    except Exception as exc:
        # catch
        # docker.errors.ContainerError – If the container exits with a non-zero exit code and detach is False.
        # docker.errors.ImageNotFound – If the specified image does not exist.
        # docker.errors.APIError – If the server returns an error.
        raise exc

    yield container

    container.remove(v=True)
