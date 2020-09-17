import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from core.api_key import API_KEY_LENGTH
from core.models.base import base


class User(base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    jobs = relationship("Job", back_populates="user", lazy='dynamic')
    owned_workspaces = relationship("Workspace", back_populates="owner", lazy='dynamic')
    email = Column(String(64), unique=True, index=True)
    api_key = Column(String(API_KEY_LENGTH), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    @staticmethod
    def get_user_from_id(user_id, session):
        return session.query(User).filter(User.id == user_id).one_or_none()

    @staticmethod
    def get_user_from_api_key(api_key, session):
        return session.query(User).filter(User.api_key == api_key).one_or_none()

    @staticmethod
    def get_user_from_email(email, session):
        return session.query(User).filter(User.email == email).one_or_none()

    def __repr__(self):
        return '<User %r>' % self.id
