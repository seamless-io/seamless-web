import os
import enum
import logging
import json

from typing import Optional, Dict, Any

import stripe

from core.models import db_commit, get_db_session
from core.models.users import User


class Product(enum.Enum):
    """
    Product names created in stripe
    """
    JOB = 'jobs'


def create_customer(user_email: str) -> str:
    """
    Should be called when user enters his credit card info
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


def process_event(request_body):
    """
    Processing stripe webhook event
    """
    stripe.api_key = os.getenv('STRIPE_API_KEY')
    event = stripe.Event.construct_from(json.loads(request_body), os.getenv('STRIPE_API_KEY'))

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
