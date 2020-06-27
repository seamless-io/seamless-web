import datetime

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from core.db import session_scope
from core.db.models.base import base


class User(UserMixin, base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    jobs = relationship("Job", back_populates="user")

    email = Column(String(64), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.now())

    # TODO remove this if we continue using Auth0
    password_hash = Column(String(128))

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    # TODO remove this if we continue using Auth0 ^^^^^^^^^^^^^^^

    def __repr__(self):
        return '<User %r>' % self.email


def load_user(user_id):
    with session_scope() as session:
        return session.query(User).get(int(user_id))
