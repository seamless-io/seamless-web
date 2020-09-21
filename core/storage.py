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
from typing import DefaultDict

import boto3

from constants import ARCHIVE_EXTENSION


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
    return current_file_version[type_][id_] != _get_md5sum_from_s3(type_, id_)
