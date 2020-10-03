import datetime
import enum
from dataclasses import dataclass

from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, Boolean, Numeric
from sqlalchemy.orm import relationship

from core.models.base import base


class WorkspacePlan(base):
    """
    This plan includes user paying 15$ a month for a Workspace created
    """
    __tablename__ = 'workspace_plans'

    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey('subscriptions.id'))
    workspace_id = Column(Integer, ForeignKey('workspaces.id'))

    subscription = relationship("Subscription")
    workspace = relationship("Workspace", back_populates="plan")

    # in case when downgrade happened - we will use this field to determine when cut off a user from services
    # TODO: when payment is over - archive workspace with a possibility to download code for 1 month, then -delete
    active = Column(Boolean)

    charges = relationship("WorkspaceCharge", back_populates='plan')

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<Plan %r %r>' % (self.id, self.name)


class WorkspaceCharge(base):
    """
    When new payment period starts or a user starts using the service - this instance is going to be created
    """
    __tablename__ = 'workspace_charges'

    id = Column(Integer, primary_key=True)

    plan_id = Column(Integer, ForeignKey('workspace_plans.id'))
    plan = relationship("WorkspacePlan", back_populates='charges')

    price = Column(Numeric, default="15.00")
    payed = Column(Boolean, default=False)

    def __repr__(self):
        return f'<WorkspaceCharge(id={self.id}, plan_id={self.plan_id})>'


class JobPlan(base):
    """
    This plan includes user paying 5$/job/month ~ 0.17 cents in a day
    Job price calculations:
        * days_existing * 0.17 (every subscription period)

    This object is creating
    """
    __tablename__ = 'job_plans'

    id = Column(Integer, primary_key=True)

    subscription_id = Column(Integer, ForeignKey('subscriptions.id'))
    job_id = Column(Integer, ForeignKey('jobs.id'))

    job = relationship("Job")

    # we use this field to decide if we need to disable a job or not
    active = True
    charges = relationship('JobCharge', back_populates='plan')

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<JobPlan(job_id={self.job_id}, subscription_id={self.subscription_id})>"


class JobCharge(base):
    """
    Created in a day of JobPlan is active
    """
    __tablename__ = 'job_charges'

    id = Column(Integer, primary_key=True)

    plan_id = Column(Integer, ForeignKey('job_plans.id'))
    plan = relationship("WorkspacePlan", back_populates='charges')

    price = Column(Numeric, default="0.161")
    payed = Column(Boolean, default=False)

    def __repr__(self):
        return f'<JobCharge(id={self.id}, plan_id={self.plan_id})>'

