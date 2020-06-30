import os
import time
from shutil import copyfile
from threading import Thread
from typing import Iterable

import boto3
import docker
from botocore.exceptions import ClientError
from docker.errors import BuildError
from docker.types import Mount

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


def execute_and_stream_to_cloudwatch(path_to_job_files: str, job_id: str, log_stream_name: str):
    logstream = _run_container(path_to_job_files, job_id)

    def put_logs_into_cloudwatch():
        cloud_watch = boto3.client('logs', region_name=os.getenv('AWS_REGION_NAME'))
        log_group_name = '/seamless/jobs/'
        try:
            cloud_watch.create_log_group(
                logGroupName=log_group_name
            )
            cloud_watch.put_retention_policy(
                logGroupName=log_group_name,
                retentionInDays=JOB_LOGS_RETENTION_DAYS
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
                pass  # If log group already exists - it's fine
            else:
                raise e
        cloud_watch.create_log_stream(
            logGroupName=log_group_name,
            logStreamName=log_stream_name
        )

        sequence_token = None
        for line in logstream:
            log_args = {
                'logGroupName': log_group_name,
                'logStreamName': log_stream_name,
                'logEvents': [
                    {
                        'timestamp': int(round(time.time() * 1000)),
                        'message': str(line, "utf-8")
                    }
                ],

            }
            if sequence_token:
                log_args.update({
                    'sequenceToken'
                    : sequence_token
                })
            response = cloud_watch.put_log_events(**log_args)
            sequence_token = response['nextSequenceToken']

    # Put logs into cloudwatch in another thread to not block the outer function
    thread = Thread(target=put_logs_into_cloudwatch)
    thread.start()
