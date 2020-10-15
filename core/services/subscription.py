import os
import logging
import datetime
import json
import time

from typing import Dict, Any

import stripe

from core.models import db_commit, get_db_session
from core.models.jobs import Job
from core.models.users import User
from core.models.workspaces import Workspace
from core.models.subscriptions import Subscription, SubscriptionItem, SubscriptionItemType, JobUsage, PRICES_FOR_TYPE


class NoBillingInfo(Exception):
    pass


class VerificationError(Exception):
    """
    Raises when signature from the webhook request is invalid
    """
    pass


def calculate_job_usages():
    session = get_db_session()
    jobs = session.query(Job).filter(
        Job.chargeable == True,  # noqa: E712
        # we charge only jobs for 1 full day
        Job.became_chargeable <= datetime.datetime.utcnow() - datetime.timedelta(days=1)
    )
    for job in jobs:
        report_job_usage(job)


def report_job_usage(job: Job):
    """
    :job: job which was created more then 1 day ago
    """
    stripe.api_key = os.getenv('STRIPE_API_KEY')
    now_ts = time.time()
    now = datetime.datetime.utcfromtimestamp(now_ts)
    session = get_db_session()
    workspace = session.query(Workspace).filter_by(id=job.workspace_id).one()
    user = session.query(User).filter_by(id=workspace.owner_id).one()
    subscription = session.query(Subscription).filter_by(customer_id=user.customer_id).one()
    subscription_item = session.query(SubscriptionItem).filter_by(subscription_id=subscription.id,
                                                                  type=SubscriptionItemType.JOB.value).one()
    usage = session.query(JobUsage).filter_by(
        subscription_item_id=subscription_item.id,
        job_id=job.id
    ).order_by(
        JobUsage.created_at.desc()
    ).limit(1).first()
    if usage:
        if (now - usage.created_at).days >= 1:
            # we are using previous usage date and replacing date to avoid minute drifts
            stripe.SubscriptionItem.create_usage_record(
                subscription_item.id,
                quantity=1,
                timestamp=int(now_ts)
            )
            session.add(JobUsage(subscription_item_id=subscription_item.id, job_id=job.id, created_at=now))
            logging.info(f"Reported usage for job '{job.id}'. SubscriptionItem: {subscription_item.id}")
        else:
            # 24h from the previous usage didn't pass
            return
    else:
        stripe.SubscriptionItem.create_usage_record(
            subscription_item.id,
            quantity=1,
            timestamp=int(now_ts)
        )
        session.add(JobUsage(subscription_item_id=subscription_item.id, job_id=job.id, created_at=now))
        logging.info(f"Reported usage for job '{job.id}'. SubscriptionItem: {subscription_item.id}")
    db_commit()


def upsert_subscription(user: User, subscription_item_type: SubscriptionItemType):
    """
    Checks if subscription item exists. If not - creates a new one and updates subscription in stripe

    WARNING:
        If pricing changes - only new subscriptions will be updated. For updating existing ones - another function
        should be created
    """
    if not user.payment_method_id:
        raise NoBillingInfo

    stripe.api_key = os.getenv('STRIPE_API_KEY')
    price_id = PRICES_FOR_TYPE[subscription_item_type]
    customer_id = user.customer_id

    session = get_db_session()
    subscription = session.query(Subscription).filter_by(customer_id=customer_id).one_or_none()
    if subscription:
        subscription_item = session.query(SubscriptionItem).filter_by(subscription_id=subscription.id,
                                                                      type=subscription_item_type.value).one_or_none()
        if subscription_item:
            # if subscription and subscription item exist - do nothing
            return
        else:
            # update existing subscription
            subscription_item_res = stripe.SubscriptionItem.create(
                subscription=subscription.id,
                price=price_id,
            )
            session.add(SubscriptionItem(id=subscription_item_res.id, subscription_id=subscription.id, price=price_id,
                                         type=subscription_item_type.value))
    else:
        # create session with subscription item
        subscription_res = stripe.Subscription.create(
            customer=customer_id,
            items=[
                {'price': price_id}
            ]
        )
        subscription = Subscription(id=subscription_res.id, customer_id=customer_id)
        session.add(subscription)
        subscription_item_res = subscription_res['items']['data'][0]  # there will be only one subscription item created
        subscription_item = SubscriptionItem(id=subscription_item_res['id'], subscription_id=subscription_res.id,
                                             price=price_id, type=subscription_item_type.value)
        session.add(subscription_item)

    db_commit()


def create_customer(user_email: str) -> str:
    """
    Should be called on user's registration
    """
    stripe.api_key = os.getenv('STRIPE_API_KEY')
    customer = stripe.Customer.create(email=user_email)
    customer_id = customer['id']
    db_commit()
    logging.info(f"Created customer in stripe with id {customer_id}")
    return customer_id


def delete_customer(customer_id: str) -> bool:
    """
    Should be called on user deletion
    """
    stripe.api_key = os.getenv('STRIPE_API_KEY')
    rv = stripe.Customer.delete(customer_id)
    db_commit()
    logging.info(f'Customer {customer_id} was deleted from stripe')
    return rv['deleted']


def create_billing_update_session(customer_id: str, success_url: str, cancel_url: str) -> str:
    """
    When user creates/updates payment method
    """
    stripe.api_key = os.getenv('STRIPE_API_KEY')
    session_payload: Dict[str, Any] = {
        'payment_method_types': ['card'],
        'mode': 'setup',
        'customer': customer_id,
        'success_url': success_url + '?session_id={CHECKOUT_SESSION_ID}',
        'cancel_url': cancel_url
    }
    session = stripe.checkout.Session.create(**session_payload)
    return session['id']


def process_event(request_body, signature):
    """
    Processing stripe webhook event
    """
    stripe.api_key = os.getenv('STRIPE_API_KEY')
    try:
        event = stripe.Webhook.construct_event(json.loads(request_body), signature, os.getenv('STRIPE_WEBHOOK_SECRET'))
    except stripe.error.SignatureVerificationError:
        raise VerificationError("Invalid signature")

    if event.type == 'checkout.session.completed':
        _handle_session_completed(event)
    return True


def _handle_session_completed(event: stripe.Event):
    setup_intent_id = event.data.object.setup_intent
    setup_intent = stripe.SetupIntent.retrieve(setup_intent_id)

    customer_id = setup_intent.customer

    logging.info(f"Customer '{customer_id}' configured payment")

    session = get_db_session()
    user = session.query(User).filter_by(customer_id=customer_id).one()
    user.payment_method_id = setup_intent.payment_method
    db_commit()
