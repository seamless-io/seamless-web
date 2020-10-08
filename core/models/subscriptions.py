from core.models.base import base

from sqlalchemy import Column, Text, ForeignKey
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

    def __repr__(self):
        return f"<Subscription(id={self.id})>"
