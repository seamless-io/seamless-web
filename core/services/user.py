from flask import session
from sqlalchemy.orm.exc import NoResultFound

from core.models.users import User
from core.web import get_db_session


class UserNotFoundException(Exception):
    pass


def get(api_key: str):
    try:
        user = User.get_user_from_api_key(api_key, get_db_session())
    except NoResultFound:
        raise UserNotFoundException('API Key is wrong, please go to our account https://app.seamlesscloud.io/account,'
                                    ' copy the API Key field and run "smls init <api key>"', 400)
    return user


def is_valid_user(job_id: str) -> str:
    """
    Validates the current user to get information about the current job.
    If a user is not valid, it returns an empty string, otherwise - his API key.
    """
    email = session['profile']['email']
    user = User.get_user_from_email(email, get_db_session())
    user_jobs = [job.id for job in user.jobs]

    # If the job does not belong to the current user, returns "Not found", 404.
    if int(job_id) not in user_jobs:
        return ''

    return user.api_key
