# TODO: all errors from executor internal functionality should be caught and processed accordingly
# TODO: add periodic task to clean-up images: docker_client.images.prune(filters={'dangling': True})
import logging
import os
import contextlib
from datetime import datetime
from threading import Thread
from typing import Iterable, List, Optional

import docker
from docker.errors import BuildError
from docker.models.containers import Container
from docker.types import Mount
from flask import current_app
from flask_socketio import emit

from backend.db import session_scope
from backend.db.models.job_run_logs import JobRunLog
from backend.db.models.job_runs import JobRunResult, JobRun
from backend.db.models.jobs import JobStatus, Job
from backend.helpers import thread_wrapper
from job_executor.project import restore_project_from_s3
from .exceptions import ExecutorBuildException

DOCKER_FILE_NAME = "Dockerfile"
REQUIREMENTS_FILENAME = "requirements.txt"
JOB_LOGS_RETENTION_DAYS = 1


class ExecutorResult:
    output = None
    exit_code = None

    def __init__(self, output, exit_code):
        self.output = output
        self.exit_code = exit_code


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


def _wait_for_exit_code(container):
    result = container.wait()
    return result["StatusCode"]


def _capture_stderr(container):
    logs = container.logs(stream=True, stdout=False, stderr=True)
    return logs


def execute_and_stream_back(path_to_job_files: str, api_key: str, entrypoint: str, requirements: str) -> Iterable[bytes]:
    try:
        container = _run_container(path_to_job_files, api_key, entrypoint, requirements)

        # We actually use only element [0] which will be the exit code of the container
        res: List[int] = []
        thread_in_thread = Thread(target=thread_wrapper,
                                  args=(_wait_for_exit_code, (container,), res))
        thread_in_thread.start()

        # We actually use only element [0] which will be the list of logs from container's stderr
        res_2: List[List[str]] = []
        thread_in_thread_2 = Thread(target=thread_wrapper,
                                    args=(_capture_stderr, (container,), res_2))
        thread_in_thread_2.start()

        # Print stdout first
        for line in container.logs(stream=True, stdout=True, stderr=False):
            yield line.decode('utf8')

        # Wait for error logs if there are some and output them only after stdout is finished
        # Otherwise log records will be mixed with each other because stdout and stderr use different buffers
        thread_in_thread_2.join()
        error_logs = res_2[0]
        for line in error_logs:
            yield line

        # Wait for container to stop and get the exit code
        thread_in_thread.join()
        exit_code = res[0]
        if exit_code != 0:
            message = f"Job failed with the exit code {exit_code}\n"
            yield message.encode()
    except BuildError as e:
        yield b"Job build failed! Error logs:\n"
        for log_entry in e.build_log:
            line = log_entry.get('stream')
            if line:
                yield line
        yield str(e).encode()


def execute_and_stream_to_db(path_to_job_files: str, job_id: str, job_run_id: str, entrypoint: str, requirements: str):
    def handle_log_line(l, app, db_session):
        # Streaming logs line by line
        with app.app_context():
            emit(
                'logs',
                {'job_id': job_id, 'message': l, 'timestamp': str(datetime.utcnow())},
                namespace='/socket',
                broadcast=True
            )
        db_session.add(
            JobRunLog(
                job_run_id=job_run_id,
                timestamp=datetime.utcnow(),
                message=l
            )
        )
        db_session.commit()

    def run_in_thread(app):
        if not os.path.exists(path_to_job_files):
            restore_project_from_s3(path_to_job_files, job_id)

        with session_scope() as db_session:
            try:
                container = _run_container(path_to_job_files, job_id, entrypoint, requirements)

                res = []
                thread_in_thread = Thread(target=thread_wrapper,
                                          args=(_wait_for_exit_code, (container,), res))
                thread_in_thread.start()

                res_2 = []
                thread_in_thread_2 = Thread(target=thread_wrapper,
                                            args=(_capture_stderr, (container,), res_2))
                thread_in_thread_2.start()


                job_run_result = JobRunResult.Ok
                job_status = JobStatus.Ok
                # Save stdout first
                for line in container.logs(stream=True, stdout=True, stderr=False):
                    l = str(line, "utf-8")
                    handle_log_line(l, app, db_session)

                # Wait for error logs if there are some and output them only after stdout is finished
                # Otherwise log records will be mixed with each other because stdout and stderr use different buffers
                thread_in_thread_2.join()
                error_logs = res_2[0]
                for line in error_logs:
                    l = str(line, "utf-8")
                    handle_log_line(l, app, db_session)

                    # Wait for container to stop and get the exit code
                thread_in_thread.join()
                status_code = res[0]
                if status_code != 0:
                    message = f"Job failed with the exit code {status_code}\n"
                    handle_log_line(message, app, db_session)
                    job_run_result = JobRunResult.Failed
                    job_status = JobStatus.Failed

            except BuildError as e:
                handle_log_line(f"Job {job_id} build failed! Error logs:\n", app, db_session)
                for log_entry in e.build_log:
                    line = log_entry.get('stream')
                    if line:
                        handle_log_line(line, app, db_session)
                job_run_result = JobRunResult.Failed
                job_status = JobStatus.Failed
            except Exception as e:
                logging.error(f"Job {job_id} failed with error {str(e)}")
                raise e

            job = db_session.query(Job).get(job_id)
            job_run = db_session.query(JobRun).get(job_run_id)
            job.status = job_status.value
            job_run.status = job_run_result.value
            db_session.commit()

            # Streaming status
            with app.app_context():
                emit('status', {'job_id': job_id,
                                'job_run_id': job_run_id,
                                'status': job_status.value},
                     namespace='/socket',
                     broadcast=True)

    thread = Thread(target=run_in_thread, kwargs={'app': current_app._get_current_object()})
    thread.start()


def execute(path_to_job_files: str,
            entrypoint: str,
            path_to_requirements: Optional[str] = None) -> ExecutorResult:
    """
    Execting in docker container
    :param path_to_job_files: path to job files
    :param entrypoint: entrypoint provided by a user
    :param path_to_requirements: path to requiremenbts provided by a user
    :return Iterable[str]
    """
    # TODO: make separation between requirements_absolute and relative
    path_to_entrypoint_file = _create_python_entrypoint_script(path_to_job_files, entrypoint)
    requirements_path = _ensure_requirements(path_to_job_files, path_to_requirements)
    with _run_container(path_to_job_files, path_to_entrypoint_file, requirements_path) as container:
        return ExecutorResult(
            (str(log, 'utf-8') for log in container.logs(stream=True)),
            container.wait()['StatusCode']
        )



def _create_python_entrypoint_script(path_to_job_files: str, entrypoint: str) -> str:
    """
    Create file which contains call to the code user provided as an entrypoint
    """
    entrypoint_file_name = "__start_smls__.py"
    entrypoint_contents = f"""
import importlib

if "." in '{entrypoint}':
    module = importlib.import_module('{entrypoint.split('.')[0]}')
    module.{'.'.join(entrypoint.split('.')[1:])}()
else:
    {entrypoint}()
    """
    with open(os.path.join(path_to_job_files, entrypoint_file_name), 'w') as entrypoint_file:
        entrypoint_file.write(entrypoint_contents)
    return entrypoint_file_name
