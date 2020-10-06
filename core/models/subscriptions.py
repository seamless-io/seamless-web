from core.models.base import base

from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship


class Subscription(base):
    """
    Models representing user subscription
    """
    __tablename__ = 'subscriptions'

    id = Column(Text, primary_key=True)

    user_id = Column(Integer, ForeignKey('users.id', name='fk_subscriptions_user_id_users_id'), nullable=False)
    user = relationship('User', back_populates='subscription')

    def __repr__(self):
        return f"<Subscription(id={self.id})>"
