from sqlalchemy.orm.exc import NoResultFound

from core.models import get_session
from core.models.users import User


class UserNotFoundException(Exception):
    pass


def get(api_key: str):
    session = get_session()
    try:
        user = User.get_user_from_api_key(api_key, session)
    except NoResultFound:
        raise UserNotFoundException('API Key is wrong, please go to our account https://app.seamlesscloud.io/account,'
                                    ' copy the API Key field and run "smls init <api key>"', 400)

