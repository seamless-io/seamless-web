from unittest.mock import patch

import pytest

from backend.apis.auth0.users import add_user_to_db
from backend.db import session_scope
from backend.db.models import User

NUMBER_OF_TEST_USERS = 10
TASKS_PER_USER = 2
DB_PREFIX = "INTEGRATION_TEST"


@pytest.fixture(scope="session")
def create_test_users():
    with patch('backend.db.DB_PREFIX', DB_PREFIX):
        user_id = add_user_to_db('fake')
        print(f"User id: {user_id}")

        yield

        with session_scope() as session:
            deleted_objects = User.__table__.delete().where(User.id.in_([user_id]))
            session.execute(deleted_objects)
            session.commit()
