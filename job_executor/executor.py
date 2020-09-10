# TODO: all errors from executor internal functionality should be caught and processed accordingly
# TODO: add periodic task to clean-up images: docker_client.images.prune(filters={'dangling': True})
import contextlib
import logging
import os
from dataclasses import dataclass
from typing import Optional, Generator, Any, Callable, Dict

import docker
from docker.errors import BuildError
from docker.models.containers import Container
from docker.types import Mount

from constants import DEFAULT_REQUIREMENTS
from .exceptions import ExecutorBuildException

DOCKER_FILE_NAME = "Dockerfile"


@dataclass
class ExecuteResult:
    output: Generator[str, Any, None]
    get_exit_code_fn: Optional[Callable[[], int]]

    _exit_code: Optional[int]=None

    def get_exit_code(self) -> Optional[int]:
        if not self._exit_code:
            assert self.get_exit_code_fn is not None
            self._exit_code = self.get_exit_code_fn()
        return self._exit_code


@contextlib.contextmanager
def execute(path_to_job_files: str,
            entrypoint_filename: str,
            parameters: Dict[str, str],
            path_to_requirements: Optional[str] = None,
            tag: Optional[str] = None) -> Generator[ExecuteResult, Any, None]:
    """
    Executing in docker container
    :param path_to_job_files: path to job files
    :param entrypoint: entrypoint provided by a user
    :param parameters: environment variables used in the job
    :param path_to_requirements: path to requirements provided by a user
    :param tag: used to tag docker containers
    :return an instance of ExecuteResult
    """
    # TODO: make separation between requirements_absolute and relative
    check_project_path(path_to_job_files)
    if entrypoint_filename == 'function.main':
        # we need to support only `function.main` situation, since it is the only one which was present at the time
        entrypoint_filename = _legacy_entrypoint_handling(path_to_job_files, entrypoint_filename)
    else:
        check_entrypoint_file(path_to_job_files, entrypoint_filename)
    requirements_path = _ensure_requirements(path_to_job_files, path_to_requirements)
    with _run_container(path_to_job_files, entrypoint_filename, requirements_path, parameters, tag) as container:

        def get_exit_code() -> int:
            return container.wait()['StatusCode']

        yield ExecuteResult(
            (str(log, 'utf-8') for log in container.logs(stream=True)),
            get_exit_code
        )

        container.wait()


def _legacy_entrypoint_handling(path_to_job_files: str, legacy_entrypoint: str) -> str:
    """
    Previously we had a way to provide `entrypoint` as `path.to.function`.
    Now we support only "entryfile" which is executing as `python -u <entryfile>`

    This function introduce backward compatibility functionality
    """
    entrypoint_file_name = "__start_smls__.py"
    entrypoint_contents = f"""
import importlib
if "." in '{legacy_entrypoint}':
    module = importlib.import_module('{legacy_entrypoint.split('.')[0]}')
    module.{'.'.join(legacy_entrypoint.split('.')[1:])}()
else:
    exec(open("{legacy_entrypoint}.py").read())
    """
    with open(os.path.join(path_to_job_files, entrypoint_file_name), 'w') as entrypoint_file:
        entrypoint_file.write(entrypoint_contents)
    return entrypoint_file_name


def check_entrypoint_file(job_directory: str, entrypoint_filename: str):
    # TODO: possibly check if the file has allowed extension `[.py, .rs, .java]`
    if not os.path.isfile(os.path.join(job_directory, entrypoint_filename)):
        raise ExecutorBuildException(f"Path to entrypoint file is not valid: `{entrypoint_filename}`")


def check_project_path(path_to_job_files):
    if not os.path.isdir(path_to_job_files):
        raise ExecutorBuildException(f"Invalid project path directory `{path_to_job_files}` does not exist")


# TODO this check is more complicated than it should be. Some context below
# We have cases when we pass empty requirements - then we crate the requirements.txt file.
# It works for smls run. But if we publish and run using the button - it was breaking because
# in db we save records with default requirements.txt, so requirements variable was not empty and
# it could not find the file.
def _ensure_requirements(job_directory: str, requirements: Optional[str]):
    """
    Dockerfile execute `ADD` operations with requirements. So, we are ensuring that it exists
    """
    # path_to_requirements = f"{job_directory}/{requirements}"
    if requirements is not None and requirements != DEFAULT_REQUIREMENTS:
        # path to requirements was provided by user and it's not a default one
        path_to_requirements = os.path.join(job_directory, requirements)
        if not os.path.exists(path_to_requirements):
            raise ExecutorBuildException(f"Cannot find requirements file `{requirements}`")
        else:
            relative_requirements_path = requirements
    else:
        # path was not provided by a user explicitly - create empty `requirements.txt`
        relative_requirements_path = 'requirements.txt'
        path_to_requirements = os.path.join(job_directory, 'requirements.txt')
        with open(path_to_requirements, 'w'):
            pass

    return relative_requirements_path


@contextlib.contextmanager
def _run_container(job_directory: str,
                   entrypoint_filename: str,
                   path_to_requirements: str,
                   parameters: Dict[str, str],
                   tag: Optional[str]) -> Container:
    dockerfile_contents = f"""
FROM python:3.8-slim
WORKDIR /src
ADD {path_to_requirements} /src/requirements.txt
RUN pip install -r requirements.txt
"""
    docker_client = docker.from_env()
    with open(os.path.join(job_directory, DOCKER_FILE_NAME), 'w') as dockerfile:
        dockerfile.write(dockerfile_contents)
    try:
        image, logs = docker_client.images.build(
            path=job_directory)
    except BuildError as e:
        full_error_log = []
        for log_entry in e.build_log:
            line = log_entry.get('stream')
            if line:
                full_error_log.append(line)

        # Log error for internal debugging
        logging.error(e)
        logging.error('\n'.join(full_error_log))

        # Raise error to show back to user
        user_visible_error_log = []
        for line in full_error_log:
            # Docker outputs a lot of it's internal build logs, the user only needs
            # to know about lines marked with ERROR
            if 'ERROR' in line:
                # Get rid of code that makes console output colorful
                if line.startswith('\x1b[91m'):
                    line = line[5:]
                if line.endswith('\x1b[0m'):
                    line = line[:-5]
                user_visible_error_log.append(line)
        raise ExecutorBuildException('\n'.join(user_visible_error_log))

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
            name=tag,
            environment=parameters
        )
    except Exception as exc:
        # catch
        # docker.errors.ContainerError – If the container exits with a non-zero exit code and detach is False.
        # docker.errors.ImageNotFound – If the specified image does not exist.
        # docker.errors.APIError – If the server returns an error.
        raise exc

    yield container

    container.remove(v=True)
