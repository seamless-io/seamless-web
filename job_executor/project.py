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

ALLOWED_EXTENSION = "tar.gz"
UPLOAD_FOLDER = "user_projects"
DATETIME_FOLDER_NAME_FORMAT = "%m_%d_%Y_%H_%M_%S"

s3 = boto3.client('s3', region_name=os.getenv('AWS_REGION_NAME'))
USER_PROJECTS_S3_BUCKET = f"web-{os.getenv('STAGE', 'local')}-jobs"


class JobType(Enum):
    RUN = 'run'
    PUBLISHED = 'published'


def get_path_to_job(job_type: JobType,
                    api_key: str,
                    job_id: Optional[str],
                    restore_from_s3_if_not_exists: bool = True):
    user_folder_path = str(os.path.join(UPLOAD_FOLDER, job_type.value, api_key))
    if job_type == JobType.PUBLISHED:
        if not job_id:
            raise Exception("If job_type = JobType.PUBLISHED you need to provide job_id")
        # Add project because there may be multiple published projects
        user_folder_path = str(os.path.join(user_folder_path, str(job_id)))

    path_to_job_files = os.path.abspath(user_folder_path)
    if job_type == JobType.PUBLISHED and restore_from_s3_if_not_exists:
        _restore_project_if_not_exists(path_to_job_files, job_id)

    return os.path.abspath(user_folder_path)


def _restore_project_if_not_exists(path_to_job_files: str, job_id: Optional[str]):
    """
    Creates a folder with user's jobs in `user_projects` folder if it is not exists.
    """
    if not os.path.exists(path_to_job_files):
        restore_project_from_s3(path_to_job_files, job_id)


def save_project_to_s3(fileobj, job_id):
    s3.upload_fileobj(Fileobj=fileobj,
                      Bucket=USER_PROJECTS_S3_BUCKET,
                      Key=f"{job_id}.{ALLOWED_EXTENSION}")
    logging.info(f"Files of job {job_id} saved to {USER_PROJECTS_S3_BUCKET} s3 bucket")


def remove_project_from_s3(job_id):
    s3.delete_object(Bucket=USER_PROJECTS_S3_BUCKET,
                     Key=f"{job_id}.{ALLOWED_EXTENSION}")
    logging.info(f"Files of job {job_id} removed from {USER_PROJECTS_S3_BUCKET} s3 bucket")


def read_bytes_from_sent_file(fileobj: FileStorage) -> io.BytesIO:
    if fileobj.filename and not fileobj.filename.endswith(ALLOWED_EXTENSION):
        raise ProjectValidationError('File extension is not allowed')
    return io.BytesIO(fileobj.read())


def create(project_file: io.BytesIO,
           api_key: str,
           job_type: JobType,
           job_id: Optional[str] = None):

    path = get_path_to_job(job_type, api_key, job_id, restore_from_s3_if_not_exists=False)
    if os.path.exists(path):
        shutil.rmtree(path)  # Remove previously created project
    Path(path).mkdir(parents=True, exist_ok=True)

    tar = tarfile.open(fileobj=project_file, mode='r')
    tar.extractall(path=path)
    tar.close()

    if job_id:
        project_file.seek(0)
        save_project_to_s3(project_file, job_id)

    logging.info(f"File saved to {path}")
    return path


def fetch_project_from_s3(job_id: Optional[str]) -> io.BytesIO:
    s3_response_object = s3.get_object(Bucket=USER_PROJECTS_S3_BUCKET,
                                       Key=f"{job_id}.{ALLOWED_EXTENSION}")
    return io.BytesIO(s3_response_object['Body'].read())


def restore_project_from_s3(path_to_job_files: str, job_id: Optional[str]):
    Path(path_to_job_files).mkdir(parents=True, exist_ok=True)
    io_bytes = fetch_project_from_s3(job_id)
    tar = tarfile.open(fileobj=io_bytes, mode='r')
    tar.extractall(path=path_to_job_files)
    tar.close()


def _extract_file_path(path: str, api_key: str, job_id: str) -> str:
    """
    To be able to get a file content that is in a subfolder, we need to have a file path inside a job project folder.
    For example, if the absolute path is '/var/seamless-web/user_projects/published/930a3944b22b16e9c170/53/some-folder/test.py',
    then the file path should be 'some-folder/test.py'.
    """
    # TODO: you're are welcome to refactore it, if you know a simpler solution.

    sep = f'{api_key}/{job_id}'
    return path[path.find(sep) + len(sep) + 1:]


def converts_folder_tree_to_dict(path, api_key, job_id):
    """
    Represents a repository tree as a dictionary. It does recursive descending into directories and build a dict.

    Returns:
        [
            {
                "content": "smls",
                "name": "requirements.txt",
                "type": "file"
            },
            {
                "name": "my-folder",
                "type": "folder",
                "children": [
                    {
                        "content": "print('Hello World!')",
                        "name": "test.py",
                        "type": "file"
                    },
                    ...
                ]
            }
        ]

    """
    d = {'name': os.path.basename(path)}
    if os.path.isdir(path):
        d['type'] = 'folder'
        d['children'] = [converts_folder_tree_to_dict(os.path.join(path, x), api_key, job_id) for x in os.listdir(path)]
    else:
        d['type'] = 'file'
        d['path'] = _extract_file_path(path, api_key, job_id)
    return d


def generate_project_structure(job_id: str, api_key: str) -> list:
    """
    Converts a folder into a list of nested dicts.
    """
    path_to_job_files = get_path_to_job(JobType.PUBLISHED, api_key, job_id)
    project_dict = converts_folder_tree_to_dict(path_to_job_files, api_key, job_id)

    return project_dict['children']


def get_file_content(job_id: str, api_key: str, file_path: str) -> Optional[str]:
    """
    Reads a content of a file as a string.
    """
    path_to_job_files = get_path_to_job(JobType.PUBLISHED, api_key, job_id)
    path_to_file = f'{path_to_job_files}/{file_path}'
    with open(path_to_file, 'r') as file:
        file_content = file.read()

    return file_content


class ProjectValidationError(Exception):
    pass
