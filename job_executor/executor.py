import os
from pathlib import Path
from shutil import copyfile
from typing import Iterable

import docker
from docker.errors import BuildError
from docker.types import Mount


DOCKER_FILE_NAME = "Dockerfile"


def execute(project_path: str, api_key: str) -> Iterable[bytes]:
    docker_client = docker.from_env()
    copyfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), DOCKER_FILE_NAME),
             os.path.join(project_path, DOCKER_FILE_NAME))
    try:
        image, logs = docker_client.images.build(
            path=project_path,
            tag=api_key)
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
                      source=project_path,
                      type='bind')],
        auto_remove=True,
        detach=True,
        mem_limit='128m',
        memswap_limit='128m'
    )
    for line in container.logs(stream=True):
        yield line
