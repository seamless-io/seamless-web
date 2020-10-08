import datetime

from core.models.base import base

from sqlalchemy import Column, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship


class Subscription(base):
    """
    Models representing user subscription
    """
    __tablename__ = 'subscriptions'

    id = Column(Text, primary_key=True)

    customer_id = Column(Text, ForeignKey('users.customer_id',
                                          name='fk_subscriptions_customer_id_users_customer_id'), nullable=False)
    user = relationship('User', back_populates='subscription')

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<Subscription(id={self.id})>"
