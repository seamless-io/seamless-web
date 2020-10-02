import datetime
import enum

from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from core.models.base import base


class SubscriptionName(enum.Enum):
    Personal = "Personal"
    Startup = "Startup"
    Business = "Business"


class Subscription(base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="subscriptions")

    name = Column(Text, nullable=False)  # Use only SubscriptionName values
    stripe_subscription_id = Column(Text)
    paid_until = Column(DateTime)
    trial_end = Column(DateTime)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<Subscription id: %r user_id: %r is_active:%r>' % (self.id, self.user_id, self.subscription_is_active)
