"""
This module is responsible for cached files storage.
It ensures that files are stored in s3 but also cached locally on the server.
The local cache is always kept in sync with the latest file on s3.
If you want to use this module - please add a new Type and create corresponding s3 buckets in Terraform.
"""
import io
import logging
import os
import shutil
import tarfile
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import DefaultDict, Optional

import boto3

from constants import ARCHIVE_EXTENSION
from job_executor.executor import DOCKER_FILE_NAME


class Type(Enum):
    Job = 'jobs'
    Template = 'job-templates'


s3 = boto3.client('s3', region_name=os.getenv('AWS_REGION_NAME'))

# Here we store the md5 sum of the latest version of files we have locally
# Each time files are requested we need to fetch md5 sum from s3
# And if it's different - we need to update local files
# The structure of the dict below is {Type : {id : md5}}
current_file_version: DefaultDict[Type, DefaultDict[str, str]] = defaultdict(lambda: defaultdict())


def get_path_to_files(type_: Type, id_: str):
    path = _get_path(type_, id_)
    if not os.path.exists(path) or _local_files_are_outdated(type_, id_):
        _restore_file_from_s3(type_, path, id_)
        current_file_version[type_][id_] = _get_md5sum_from_s3(type_, id_)
    return path


def save(file: io.BytesIO, type_: Type, id_: str):
    path = _get_path(type_, id_)
    if os.path.exists(path):
        shutil.rmtree(path)  # Remove previously created project
    Path(path).mkdir(parents=True, exist_ok=True)

    _extract_archive_into_folder(file, path)
    file.seek(0)
    _save_file_to_s3(file, type_, id_)

    current_file_version[type_][id_] = _get_md5sum_from_s3(type_, id_)

    logging.info(f"Created files with id {id_}, type {type_.value} and path {path}")
    return path


def delete(type_: Type, id_: str):
    path_to_files = _get_path(type_, id_)
    if os.path.exists(path_to_files):
        shutil.rmtree(path_to_files)

    _remove_file_from_s3(type_, id_)

    if current_file_version.get(type_):
        if current_file_version[type_].get(id_):
            del current_file_version[type_][id_]


def get_archive(type_: Type, id_: str):
    return _fetch_file_from_s3(type_, id_)


def init():
    """
    used when we start the web application to make sure everything in the local file system is clean
    """
    for t in Type:
        path_to_files = os.path.abspath(_get_folder_name(t))
        if os.path.exists(path_to_files):
            shutil.rmtree(path_to_files)


def generate_project_structure(type_: Type, id_: str) -> list:
    """
    Converts a folder into a list of nested dicts.
    """
    path_to_files = get_path_to_files(type_, id_)
    project_dict = _file_tree_to_dict(path_to_files, id_)['children']
    if type_ == Type.Job:
        # In order to run Jobs we add Docker file to their files. We need to hide it for the user.
        project_dict = [child for child in project_dict if child['name'] != DOCKER_FILE_NAME]

    return project_dict


def get_file_content(type_: Type, id_: str, file_path: str) -> Optional[str]:
    """
    Reads a content of a file as a string.
    """
    path_to_job_files = get_path_to_files(type_, id_)
    path_to_file = f'{path_to_job_files}/{file_path}'
    with open(path_to_file, 'r') as file:
        file_content = file.read()

    return file_content


def _get_path(type_: Type, id_: str):
    return os.path.abspath(str(os.path.join(_get_folder_name(type_), id_)))


def _get_s3_bucket_name(type_: Type):
    return f"web-{os.getenv('STAGE', 'local')}-{type_.value}"


def _get_folder_name(type_: Type):
    return _get_s3_bucket_name(type_)  # Same name for folder as for s3 bucket (for simplicity)


def _restore_file_from_s3(type_: Type, path: str, id_: str):
    Path(path).mkdir(parents=True, exist_ok=True)
    io_bytes = _fetch_file_from_s3(type_, id_)
    _extract_archive_into_folder(io_bytes, path)
    logging.info(f"Restored {type_.value} {id_} files from s3")


def _fetch_file_from_s3(type_: Type, id_: str) -> io.BytesIO:
    s3_response_object = s3.get_object(Bucket=_get_s3_bucket_name(type_),
                                       Key=f"{id_}.{ARCHIVE_EXTENSION}")
    return io.BytesIO(s3_response_object['Body'].read())


def _save_file_to_s3(fileobj: io.BytesIO, type_: Type, id_: str):
    s3.upload_fileobj(Fileobj=fileobj,
                      Bucket=_get_s3_bucket_name(type_),
                      Key=f"{id_}.{ARCHIVE_EXTENSION}")
    logging.info(f"{type_.value} file saved to {_get_s3_bucket_name(type_)} s3 bucket under id {id_} ")


def _remove_file_from_s3(type_: Type, id_: str):
    s3.delete_object(Bucket=_get_s3_bucket_name(type_),
                     Key=f"{id_}.{ARCHIVE_EXTENSION}")
    logging.info(f"{type_.value} file removed from {_get_s3_bucket_name(type_)} s3 bucket under id {id_} ")


def _extract_archive_into_folder(archive: io.BytesIO, path: str):
    tar = tarfile.open(fileobj=archive, mode='r')
    tar.extractall(path=path)
    tar.close()


def _get_md5sum_from_s3(type_: Type, id_: str):
    """
    https://stackoverflow.com/questions/26415923/boto-get-md5-s3-file
    """
    return s3.head_object(Bucket=_get_s3_bucket_name(type_),
                          Key=f"{id_}.{ARCHIVE_EXTENSION}")['ETag'][1:-1]


def _local_files_are_outdated(type_: Type, id_: str):
    if current_file_version.get(type_):
        if current_file_version[type_].get(id_):
            return current_file_version[type_][id_] != _get_md5sum_from_s3(type_, id_)
    return True


def _extract_file_path(path: str, id_: str) -> str:
    """
    To be able to get a file content that is in a subfolder, we need to have a file path inside a job project folder.
    For example, if the absolute path is '/var/seamless-web/user_projects/published/930a3944b22b16e9c170/53/some-folder/test.py',
    then the file path should be 'some-folder/test.py'.
    """
    # TODO: you're are welcome to refactor it, if you know a simpler solution.

    sep = f'{id_}'
    return path[path.find(sep) + len(sep) + 1:]


def _file_tree_to_dict(path, id_: str):
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
        d['children'] = [_file_tree_to_dict(str(os.path.join(path, x)), id_)
                         for x in os.listdir(path)]
    else:
        d['type'] = 'file'
        d['path'] = _extract_file_path(path, id_)
    return d
