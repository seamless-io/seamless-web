import os
from datetime import datetime
from shutil import copyfile
from threading import Thread
from typing import Iterable

import docker
from docker.errors import BuildError
from docker.types import Mount

from backend.db import session_scope
from backend.db.models.job_run_logs import JobRunLog

DOCKER_FILE_NAME = "Dockerfile"
JOB_LOGS_RETENTION_DAYS = 1


def _run_container(path_to_job_files: str, tag: str) -> Iterable[bytes]:
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
            if line and "ERROR:" in line:
                error_logs.append(line.rstrip('\n'))
        return error_logs

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
    return container.logs(stream=True)


def execute_and_stream_back(path_to_job_files: str, api_key: str) -> Iterable[bytes]:
    logstream = _run_container(path_to_job_files, api_key)
    for line in logstream:
        yield line


def execute_and_stream_to_db(path_to_job_files: str, job_id: str, job_run_id: str, ):
    logstream = _run_container(path_to_job_files, job_id)

    def save_logs():
        with session_scope() as db_session:
            for line in logstream:
                db_session.add(
                    JobRunLog(
                        job_run_id=job_run_id,
                        timestamp=datetime.utcnow(),
                        message=str(line, "utf-8")
                    )
                )
                db_session.commit()

    # Put logs into cloudwatch in another thread to not block the outer function
    thread = Thread(target=save_logs)
    thread.start()
