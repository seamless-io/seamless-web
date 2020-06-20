import datetime

from sqlalchemy import Column, Integer, DateTime

from core.db_passwords.models.base import base


class Password(base):
    __tablename__ = 'passwords'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<User id %r>' % self.user_id
