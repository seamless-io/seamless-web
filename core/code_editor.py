import os
from typing import Optional

from core.storage import get_path_to_files, Type


def _extract_file_path(path: str, job_id: str) -> str:
    """
    To be able to get a file content that is in a subfolder, we need to have a file path inside a job project folder.
    For example, if the absolute path is '/var/seamless-web/user_projects/published/930a3944b22b16e9c170/53/some-folder/test.py',
    then the file path should be 'some-folder/test.py'.
    """
    # TODO: you're are welcome to refactore it, if you know a simpler solution.

    sep = f'{job_id}'
    return path[path.find(sep) + len(sep) + 1:]


def converts_folder_tree_to_dict(path, job_id):
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
        d['children'] = [converts_folder_tree_to_dict(os.path.join(path, x), job_id)
                         for x in os.listdir(path)]
    else:
        d['type'] = 'file'
        d['path'] = _extract_file_path(path, job_id)
    return d


def generate_project_structure(job_id: str) -> list:
    """
    Converts a folder into a list of nested dicts.
    """
    path_to_job_files = get_path_to_files(Type.Job, job_id)
    project_dict = converts_folder_tree_to_dict(path_to_job_files, job_id)

    return project_dict['children']


def get_file_content(job_id: str, file_path: str) -> Optional[str]:
    """
    Reads a content of a file as a string.
    """
    path_to_job_files = get_path_to_files(Type.Job, job_id)
    path_to_file = f'{path_to_job_files}/{file_path}'
    with open(path_to_file, 'r') as file:
        file_content = file.read()

    return file_content



