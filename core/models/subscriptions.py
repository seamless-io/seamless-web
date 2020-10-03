import datetime
import enum

from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from core.models.base import base


class Subscription(base):
    """
    This model is keeping the payment information for a user
    """
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="subscription")

    stripe_subscription_id = Column(Text)
    paid_until = Column(DateTime)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<Subscription id: %r user_id: %r is_active:%r>' % (self.id, self.user_id, self.subscription_is_active)
