import os
import enum
import logging
import json

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
