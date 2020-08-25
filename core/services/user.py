from sqlalchemy.orm.exc import NoResultFound

from core.models.users import User
from core.web import db_session


class UserNotFoundException(Exception):
    pass


def get(api_key: str):
    try:
        user = User.get_user_from_api_key(api_key, db_session)
    except NoResultFound:
        raise UserNotFoundException('API Key is wrong, please go to our account https://app.seamlesscloud.io/account,'
                                    ' copy the API Key field and run "smls init <api key>"', 400)
    return user
