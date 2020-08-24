from unittest.mock import patch

import pytest

from core.api_key import generate_api_key
from core.helpers import row2dict
from core.models import session_scope
from core.models.users import User

NUMBER_OF_TEST_USERS = 2
DB_PREFIX = "INTEGRATION_TEST"


@pytest.fixture(scope="session")
def test_users():
    with patch('core.db.DB_PREFIX', DB_PREFIX):
        with session_scope() as db_session:
            users = [User(email=f"{i}@loadtest.com", api_key=generate_api_key())
                     for i in range(NUMBER_OF_TEST_USERS)]
            for user in users:
                db_session.add(user)
            db_session.commit()

            yield [row2dict(user) for user in users]

            for user in users:
                db_session.delete(user)
            db_session.commit()
