import os
import enum
import datetime

from core.models.base import base

from sqlalchemy import Column, Text, ForeignKey, DateTime, Integer
from sqlalchemy.orm import relationship


class SubscriptionItemType(enum.Enum):
    JOB = 'job'


PRICES_FOR_TYPE = {
    SubscriptionItemType.JOB: os.getenv('JOB_PRICE_ID')
}


class Subscription(base):
    """
    Models representing user subscription
    """
    __tablename__ = 'subscriptions'

    id = Column(Text, primary_key=True)

    customer_id = Column(Text, ForeignKey('users.customer_id',
                                          name='fk_subscriptions_customer_id_users_customer_id'), nullable=False)
    user = relationship('User', back_populates='subscription')

    items = relationship('SubscriptionItem', back_populates='subscription')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<Subscription(id={self.id})>"


class SubscriptionItem(base):
    """
    Representing SubscriptionItem for Job
    """
    __tablename__ = 'subscription_items'

    id = Column(Text, primary_key=True)

    type = Column(Text, nullable=False)  # use SubscriptionItemType enum

    subscription_id = Column(Text, ForeignKey('subscriptions.id'), nullable=False)
    subscription = relationship('Subscription', back_populates='items')

    price = Column(Text, default=os.getenv('JOB_PRICE_ID'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    usages = relationship('JobUsage', back_populates='subscription_item')

    def __repr__(self):
        return f"<SubscriptionItem(id='{self.id}', subscription_id='{self.subscription_id}')>"


class JobUsage(base):
    """
    This model holds information about 1 job existing for 1 day
    """
    __tablename__ = 'job_usages'

    id = Column(Integer, primary_key=True)

    subscription_item_id = Column(Text, ForeignKey('subscription_items.id'), nullable=False)
    subscription_item = relationship('SubscriptionItem', back_populates='usages')

    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=True)
    job = relationship('Job', back_populates='usages')

    created_at = Column(DateTime)

    def __repr__(self):
        return f"<JobUsage(id='{self.id}', subscription_item_id='{self.subscription_item_id}', job_id='{self.job_id}')>"