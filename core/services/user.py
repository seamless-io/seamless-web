from sqlalchemy.orm.exc import NoResultFound

from core.api_key import generate_api_key
from core.models import get_db_session, db_commit

from core.models.users import User
from core.models.workspaces import Workspace


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


def create(email):
    db_session = get_db_session()
    user = User(email=email,
                api_key=generate_api_key())
    db_session.add(user)
    db_commit()

    workspace = Workspace(owner_id=user.id)
    db_session.add(workspace)
    db_commit()
    return user.id
