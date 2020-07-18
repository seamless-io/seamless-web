import os
from datetime import datetime
from shutil import copyfile
from threading import Thread
from typing import Iterable, Tuple

import docker
from docker.errors import BuildError
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


def _run_container(path_to_job_files: str, tag: str) -> Tuple[Iterable[bytes], bool]:
    _ensure_requirements(path_to_job_files)
    docker_client = docker.from_env()
    copyfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), DOCKER_FILE_NAME),
             os.path.join(path_to_job_files, DOCKER_FILE_NAME))
    try:
        image, logs = docker_client.images.build(
            path=path_to_job_files,
            tag=tag)
    except BuildError as e:
        error_logs = []
        for log_entry in e.build_log:
            line = log_entry.get('stream')
            if line:
                error_logs.append(line.rstrip('\n'))
        return error_logs, False

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
    return container.logs(stream=True), True


def execute_and_stream_back(path_to_job_files: str, api_key: str) -> Iterable[bytes]:
    logstream, build_successful = _run_container(path_to_job_files, api_key)
    if not build_successful:
        yield b"Job build failed!\n"
    for line in logstream:
        yield line


def execute_and_stream_to_db(path_to_job_files: str, job_id: str, job_run_id: str):
    def run_in_thread(app):
        if not os.path.exists(path_to_job_files):
            restore_project_from_s3(path_to_job_files, job_id)
        logstream, build_successful = _run_container(path_to_job_files, job_id)

        with session_scope() as db_session:
            job_run_result = JobRunResult.Ok
            job_status = JobStatus.Ok
            for line in logstream:
                l = str(line, "utf-8")
                with app.app_context():
                    emit('logs', {'log_line': l},
                         namespace='/socket',
                         broadcast=True)
                if "error" in l.lower():
                    job_run_result = JobRunResult.Failed
                    job_status = JobStatus.Failed
                db_session.add(
                    JobRunLog(
                        job_run_id=job_run_id,
                        timestamp=datetime.utcnow(),
                        message=str(line, "utf-8")
                    )
                )
                db_session.commit()
            job = db_session.query(Job).get(job_id)
            job_run = db_session.query(JobRun).get(job_run_id)
            job.status = job_status.value
            job_run.status = job_run_result.value
            db_session.commit()

            with app.app_context():
                emit('status', {'job_id': job_id,
                                'job_run_id': job_run_id,
                                'status': job_status.value},
                     namespace='/socket',
                     broadcast=True)

    thread = Thread(target=run_in_thread, kwargs={'app': current_app._get_current_object()})
    thread.start()
