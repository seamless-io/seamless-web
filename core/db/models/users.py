import datetime

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, DateTime
from werkzeug.security import generate_password_hash, check_password_hash

from core.db import session_scope
from core.db.models.base import base

# TODO remove this if we continue using Auth0


class User(UserMixin, base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(64), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    password_hash = Column(String(128))

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.email


def load_user(user_id):
    with session_scope() as session:
        return session.query(User).get(int(user_id))
