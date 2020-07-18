from unittest.mock import patch

import pytest

from backend.api_key import generate_api_key
from backend.db import session_scope
from backend.db.models import User
from backend.helpers import row2dict

NUMBER_OF_TEST_USERS = 1
JOBS_PER_USER = 1
DB_PREFIX = "INTEGRATION_TEST"


@pytest.fixture(scope="session")
def test_users():
    with patch('backend.db.DB_PREFIX', DB_PREFIX):
        with session_scope() as session:
            users = [User(email=f"{i}@loadtest.com", api_key=generate_api_key())
                     for i in range(NUMBER_OF_TEST_USERS)]
            for user in users:
                session.add(user)
            session.commit()

            yield [row2dict(user) for user in users]

            for user in users:
                session.delete(user)
            session.commit()
