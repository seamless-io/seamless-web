import io
import logging
import os
import shutil
import tarfile
from typing import List

import yaml
from werkzeug.datastructures import FileStorage

from constants import ARCHIVE_EXTENSION
from core import storage
from core.models import get_db_session, JobTemplate, db_commit
from core.storage import Type

EXTRACTED_PACKAGE_FOLDER_NAME = 'job_templates_folder'
TEMPLATES_CONFIG_FILE = 'table_of_contents.yml'


class JobTemplateNotFoundException(Exception):
    pass


def _unpack_templates_archive(templates_package: FileStorage, templates_folder: str):
    io_bytes = io.BytesIO(templates_package.read())
    tar = tarfile.open(fileobj=io_bytes, mode='r')
    tar.extractall(path=templates_folder)
    tar.close()


def _get_templates_list_from_config(templates_folder: str, templates_config_file_name: str) -> List:
    result = yaml.load(open(os.path.join(templates_folder, templates_config_file_name)),
                       Loader=yaml.FullLoader)
    logging.info(result)
    return result['templates']


def _archive_template_files(job_template_id: str, path_to_template_files: str) -> str:
    archive_location = os.path.join(path_to_template_files, f"{job_template_id}.{ARCHIVE_EXTENSION}")
    tar = tarfile.open(archive_location, "w:gz")
    tar.add(path_to_template_files, arcname='.')
    tar.close()
    return archive_location


def update_templates(templates_package):
    try:
        _unpack_templates_archive(templates_package, EXTRACTED_PACKAGE_FOLDER_NAME)
        templates_list = _get_templates_list_from_config(
            EXTRACTED_PACKAGE_FOLDER_NAME, TEMPLATES_CONFIG_FILE)

        for template_config in templates_list:
            existing_template = JobTemplate.get_template_from_name(template_config['name'],
                                                                   get_db_session())
            if existing_template:
                # Update existing record
                existing_template.short_description = template_config['short_description']
                existing_template.long_description_url = template_config['long_description_url']
                existing_template.tags = ','.join(template_config['tags'])
                template = existing_template
            else:
                # create new record
                new_template = JobTemplate(
                        name=template_config['name'],
                        short_description=template_config['short_description'],
                        long_description_url=template_config['long_description_url'],
                        tags=','.join(template_config['tags']))
                get_db_session().add(new_template)
                template = new_template
            db_commit()
            path_to_template_files = os.path.join(EXTRACTED_PACKAGE_FOLDER_NAME,
                                                  template_config['path_to_files'])
            archive_location = _archive_template_files(str(template.id), path_to_template_files)
            with open(archive_location, "rb") as f:
                storage.save(io.BytesIO(f.read()), Type.Template, str(template.id))
        # Notice that we do not delete templates automatically if we cannot find them in config
        # Deleting a template is a complex workflow (because of its dependencies) and also pretty risky
        # So for now you need to delete templates manually from the db if you need to
    finally:
        try:
            shutil.rmtree(EXTRACTED_PACKAGE_FOLDER_NAME)
        except OSError:
            pass


def get_template(template_id):
    job_template = get_db_session().query(JobTemplate).filter_by(id=template_id).one_or_none()

    if job_template is None:
        raise JobTemplateNotFoundException(f"Job Template id:{template_id} Not Found")
    return job_template


def get_templates():
    return get_db_session().query(JobTemplate).all()


def get_template_package(template_id):
    return storage.get_archive(Type.Template, template_id)
