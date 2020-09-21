import pytest
from sqlalchemy.orm import scoped_session

from core.api_key import generate_api_key
from helpers import row2dict
from core.models import get_session_factory
from core.models.users import User

NUMBER_OF_TEST_USERS = 3
DB_PREFIX = "INTEGRATION_TEST"

db_session = scoped_session(get_session_factory(DB_PREFIX))()


@pytest.fixture(scope="session")
def test_users():
    users = [User(email=f"{i}@loadtest.com", api_key=generate_api_key())
             for i in range(NUMBER_OF_TEST_USERS)]
    for user in users:
        db_session.add(user)
    db_session.commit()

    yield [row2dict(user) for user in users]

    for user in users:
        db_session.delete(user)
    db_session.commit()
