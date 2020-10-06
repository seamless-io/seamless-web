import os
import enum
import logging
import json

from typing import Optional, Dict, Any

import stripe

from core.models import db_commit, get_db_session
from core.models.subscriptions import Subscription


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



def _create(customer_id: int, product: Product):
    """
    Creates a subscription for user for chosen products
    Calls when user buy something for a first time
    """
    pass


def add_product(subscription_id: int, product: Product):
    """
    Adds a product to subscription
    """
    pass


def remove_product(subscription_id: int, product: Product):
    """
    Removes a product from subscription
    """
    pass


def update_subscription(user_id: int):
    """
    Updates a subscription for a user
    """
    pass


def create_billing_update_session(customer_id: str, success_url: str, cancel_url: str,
                                  existing_subscription_id: Optional[str] = None) -> str:
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
    if existing_subscription_id:
        session_payload.update({
            'setup_intent_data': {
                'metadata': {'subscription_id': existing_subscription_id}
            }
        })
    session = stripe.checkout.Session.create(**session_payload)
    return session['id']


def process_event(request_body, user_id):
    """
    Processing stipe webhook event
    """
    stripe.api_key = os.getenv('STRIPE_API_KEY')
    event = stripe.Webhook.construct_from(json.loads(request_body), os.getenv('STRIPE_API_KEY'))

    if event.type == 'checkout.session.completed':
        stripe_session_obj = event.data.object
        setup_intent_id = stripe_session_obj['data']['object']['setup_intent']
        intent = stripe.SetupIntent.retrieve(setup_intent_id)

        payment_method_id = intent['payment_method']
        subscription_id = intent['subscription']

        stripe.Subscription.modify(subscription_id, default_payment_method=payment_method_id)

        session = get_db_session()
        session.add(Subscription(id=subscription_id, user_id=user_id))
        db_commit()

        return True

