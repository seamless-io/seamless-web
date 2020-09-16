from typing import Dict

from sqlalchemy.orm.exc import NoResultFound

from core.models.users import User
from core.web import get_db_session


class UserNotFoundException(Exception):
    pass


def get_by_api_key(api_key: str):
    try:
        user = User.get_user_from_api_key(api_key, get_db_session())
    except NoResultFound:
        raise UserNotFoundException('API Key is wrong, please go to our account https://app.seamlesscloud.io/account,'
                                    ' copy the API Key field and run "smls init <api key>"')
    return user


def get_by_id(user_id: str):
    try:
        user = User.get_user_from_id(user_id, get_db_session())
    except NoResultFound:
        raise UserNotFoundException(f'Cannot find a user with id: {user_id}')
    return user


def create_user(data: Dict):
    """
    Creates a "Personal" workspace (team) and ties it to the user created
    """
    pass
