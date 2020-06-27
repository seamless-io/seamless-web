import datetime

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, DateTime

from core.db import session_scope
from core.db.models.base import base


class User(UserMixin, base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(64), unique=True, index=True)
    api_key = Column(String(20), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<User %r>' % self.id


def load_user(user_id):
    with session_scope() as session:
        return session.query(User).get(int(user_id))
