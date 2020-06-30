"""
Module for manipulations with projects/jobs uploaded to seamless
"""
import os
import io
import shutil
import tarfile
import datetime
import logging
from enum import Enum
from pathlib import Path
from typing import Optional

from werkzeug.datastructures import FileStorage


ALLOWED_EXTENSION = "tar.gz"
UPLOAD_FOLDER = "user_projects"
DATETIME_FOLDER_NAME_FORMAT = "%m_%d_%Y_%H_%M_%S"


class JobType(Enum):
    RUN = 'run'
    PUBLISHED = 'published'


def get_path_to_job(job_type: JobType,
                    api_key: str,
                    job_id: Optional[str]):
    user_folder_path = str(os.path.join(UPLOAD_FOLDER, job_type.value, api_key))
    if job_type == JobType.PUBLISHED:
        # Add project because there may be multiple published projects
        user_folder_path = str(os.path.join(user_folder_path, job_id))
    return user_folder_path


def create(fileobj: FileStorage,
           api_key: str,
           job_type: JobType,
           job_id: str = None):
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

    destination = os.path.abspath(path)
    logging.info(f"File saved to {destination}")
    return destination


class ProjectValidationError(Exception):
    pass
