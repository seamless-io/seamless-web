import datetime

from sqlalchemy import Column, Integer, String, DateTime

from core.db.models.base import base


class User(base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(64), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<User %r>' % self.email
