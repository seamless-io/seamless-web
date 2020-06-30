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

from werkzeug.datastructures import FileStorage


ALLOWED_EXTENSION = "tar.gz"
UPLOAD_FOLDER = "user_projects"
DATETIME_FOLDER_NAME_FORMAT = "%m_%d_%Y_%H_%M_%S"


class ProjectType(Enum):
    RUN = 'run'
    PUBLISHED = 'published'


def create(fileobj: FileStorage, api_key: str, project_type: ProjectType):
    if fileobj.filename and not fileobj.filename.endswith(ALLOWED_EXTENSION):
        raise ProjectValidationError('File extension is not allowed')

    dest = _save_to_disk(fileobj, api_key, project_type)
    return dest


def _save_to_disk(fileobj: FileStorage, api_key: str, project_type: ProjectType) -> str:
    user_folder_path = str(os.path.join(UPLOAD_FOLDER, project_type.value, api_key))
    if os.path.exists(user_folder_path):
        shutil.rmtree(user_folder_path)  # Remove previously created project
    Path(user_folder_path).mkdir(parents=True, exist_ok=True)

    io_bytes = io.BytesIO(fileobj.read())
    tar = tarfile.open(fileobj=io_bytes, mode='r')
    tar.extractall(path=user_folder_path)
    tar.close()

    destination = os.path.abspath(user_folder_path)
    logging.info(f"File saved to {destination}")
    return destination


class ProjectValidationError(Exception):
    pass
