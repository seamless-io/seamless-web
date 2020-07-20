import os
from datetime import datetime
from shutil import copyfile
from threading import Thread
from time import sleep
from typing import Iterable, Tuple

import docker
from docker.errors import BuildError
from docker.models.containers import Container
from docker.types import Mount
from flask_socketio import emit

from flask import current_app
from backend.db import session_scope
from backend.db.models.job_run_logs import JobRunLog
from backend.db.models.job_runs import JobRunResult, JobRun
from backend.db.models.jobs import JobStatus, Job
from job_executor.project import restore_project_from_s3

DOCKER_FILE_NAME = "Dockerfile"
REQUIREMENTS_FILENAME = "requirements.txt"
JOB_LOGS_RETENTION_DAYS = 1


def _ensure_requirements(job_directory):
    """
    Dockerfile execute `ADD` operations with requirements. So, we are ensuring that it exists
    """
    path_to_requirements = f"{job_directory}/{REQUIREMENTS_FILENAME}"
    if not os.path.exists(path_to_requirements):
        with open(path_to_requirements, 'w'):
            pass


def _run_container(path_to_job_files: str, tag: str) -> Container:
    _ensure_requirements(path_to_job_files)
    docker_client = docker.from_env()
    copyfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), DOCKER_FILE_NAME),
             os.path.join(path_to_job_files, DOCKER_FILE_NAME))
    image, logs = docker_client.images.build(
        path=path_to_job_files,
        tag=tag)

    # Remove stopped containers and old images
    docker_client.containers.prune()
    docker_client.images.prune(filters={'dangling': True})

    container = docker_client.containers.run(
        image=image,
        command="bash -c \"python -u function.py\"",
        mounts=[Mount(target='/src',
                      source=path_to_job_files,
                      type='bind')],
        auto_remove=True,
        detach=True,
        mem_limit='128m',
        memswap_limit='128m'
    )
    return container


def execute_and_stream_back(path_to_job_files: str, api_key: str) -> Iterable[bytes]:
    try:
        container = _run_container(path_to_job_files, api_key)
        for line in container.logs(stream=True):
            yield line
        result = container.wait()
        status_code = result["StatusCode"]
        if status_code != 0:
            message = f"Container failed with the exit code {status_code}\n"
            yield message.encode()
    except BuildError as e:
        yield b"Job build failed! Error logs:\n"
        for log_entry in e.build_log:
            line = log_entry.get('stream')
            if line:
                yield line


def execute_and_stream_to_db(path_to_job_files: str, job_id: str, job_run_id: str):
    def handle_log_line(l, app, db_session):
        # Streaming logs line by line
        with app.app_context():
            emit(
                'logs',
                {'job_id': job_id, 'log_line': l},
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

        try:
            container = _run_container(path_to_job_files, job_id)
            with session_scope() as db_session:
                job_run_result = JobRunResult.Ok
                job_status = JobStatus.Ok
                for line in container.logs(stream=True):
                    l = str(line, "utf-8")
                    if "error" in l.lower():
                        job_run_result = JobRunResult.Failed
                        job_status = JobStatus.Failed
                    handle_log_line(l, app, db_session)
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
        except BuildError as e:
            handle_log_line(b"Job build failed! Error logs:\n", app, db_session)
            for log_entry in e.build_log:
                line = log_entry.get('stream')
                if line:
                    handle_log_line(l, app, db_session)

    thread = Thread(target=run_in_thread, kwargs={'app': current_app._get_current_object()})
    thread.start()
