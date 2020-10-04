import datetime
import enum
from dataclasses import dataclass

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship

from core.api_key import API_KEY_LENGTH
from core.models.base import base


class UserAccountType(enum.Enum):
    Free = "FREE"
    Professional = "PROFESSIONAL"


@dataclass
class AccountLimits:
    jobs: int


ACCOUNT_LIMITS_BY_TYPE = {
    UserAccountType.Free: AccountLimits(jobs=2),
    UserAccountType.Professional: AccountLimits(jobs=10)
}


class User(base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)

    jobs = relationship("Job", back_populates="user", lazy='dynamic')
    workspaces = relationship("Workspace", back_populates='owner')

    email = Column(String(64), unique=True, index=True)
    api_key = Column(String(API_KEY_LENGTH), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    account_type = Column(Text, nullable=False, default=UserAccountType.Free.value)

    @staticmethod
    def get_user_from_id(user_id, session):
        return session.query(User).filter(User.id == user_id).one()

    @staticmethod
    def get_user_from_api_key(api_key, session):
        return session.query(User).filter(User.api_key == api_key).one()

    @staticmethod
    def get_user_from_email(email, session):
        return session.query(User).filter(User.email == email).one()

    def __repr__(self):
        return '<User %r>' % self.id
