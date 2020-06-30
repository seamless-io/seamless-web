import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from backend.db import session_scope
from backend.db.models.base import base
from backend.api_key import API_KEY_LENGTH


class User(base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    jobs = relationship("Job", back_populates="user")
    email = Column(String(64), unique=True, index=True)
    api_key = Column(String(API_KEY_LENGTH), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<User %r>' % self.id


def load_user(user_id):
    with session_scope() as session:
        return session.query(User).get(int(user_id))
