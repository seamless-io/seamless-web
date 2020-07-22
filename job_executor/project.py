"""
Module for manipulations with projects/jobs uploaded to seamless
"""
import io
import logging
import os
import shutil
import tarfile
from enum import Enum
from pathlib import Path
from typing import Optional

import boto3
from werkzeug.datastructures import FileStorage

from config import STAGE

ALLOWED_EXTENSION = "tar.gz"
UPLOAD_FOLDER = "user_projects"
DATETIME_FOLDER_NAME_FORMAT = "%m_%d_%Y_%H_%M_%S"

s3 = boto3.client('s3', region_name=os.getenv('AWS_REGION_NAME'))
USER_PROJECTS_S3_BUCKET = f"web-{STAGE}-jobs"


class JobType(Enum):
    RUN = 'run'
    PUBLISHED = 'published'


def get_path_to_job(job_type: JobType,
                    api_key: str,
                    job_id: Optional[str]):
    user_folder_path = str(os.path.join(UPLOAD_FOLDER, job_type.value, api_key))
    if job_type == JobType.PUBLISHED:
        if not job_id:
            raise Exception("If job_type = JobType.PUBLISHED you need to provide job_id")
        # Add project because there may be multiple published projects
        user_folder_path = str(os.path.join(user_folder_path, job_id))
    return os.path.abspath(user_folder_path)


def save_project_to_s3(fileobj, job_id):
    s3.upload_fileobj(Fileobj=fileobj,
                      Bucket=USER_PROJECTS_S3_BUCKET,
                      Key=f"{job_id}.{ALLOWED_EXTENSION}")
    logging.info(f"Files of job {job_id} saved to {USER_PROJECTS_S3_BUCKET} s3 bucket")


def remove_project_from_s3(job_id):
    s3.delete_object(Bucket=USER_PROJECTS_S3_BUCKET,
                     Key=f"{job_id}.{ALLOWED_EXTENSION}")
    logging.info(f"Files of job {job_id} removed from {USER_PROJECTS_S3_BUCKET} s3 bucket")


def create(fileobj: FileStorage,
           api_key: str,
           job_type: JobType,
           job_id: Optional[str] = None):
    if fileobj.filename and not fileobj.filename.endswith(ALLOWED_EXTENSION):
        raise ProjectValidationError('File extension is not allowed')

    path = get_path_to_job(job_type, api_key, job_id)
    if os.path.exists(path):
        shutil.rmtree(path)  # Remove previously created project
    Path(path).mkdir(parents=True, exist_ok=True)

    io_bytes = io.BytesIO(fileobj.read())
    tar = tarfile.open(fileobj=io_bytes, mode='r')
    tar.extractall(path=path)
    tar.close()

    if job_id:
        io_bytes.seek(0)
        save_project_to_s3(io_bytes, job_id)

    logging.info(f"File saved to {path}")
    return path


def fetch_project_from_s3(job_id: str) -> io.BytesIO:
    s3_response_object = s3.get_object(Bucket=USER_PROJECTS_S3_BUCKET,
                                       Key=f"{job_id}.{ALLOWED_EXTENSION}")
    return io.BytesIO(s3_response_object['Body'].read())


def restore_project_from_s3(path_to_job_files: str, job_id: str):
    Path(path_to_job_files).mkdir(parents=True, exist_ok=True)
    io_bytes = fetch_project_from_s3(job_id)
    tar = tarfile.open(fileobj=io_bytes, mode='r')
    tar.extractall(path=path_to_job_files)
    tar.close()


class ProjectValidationError(Exception):
    pass
