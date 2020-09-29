import logging
import os
from datetime import datetime, timedelta

import stripe

from constants import SUBSCRIPTION_TRIAL_DAYS
from core.models import User, db_commit, Workspace

# Set your secret key. Remember to switch to your live secret key in production!
# See your keys here: https://dashboard.stripe.com/account/apikeys
stripe.api_key = os.getenv('STRIPE_API_KEY')


class MultiplePricesOfProductError(Exception):
    pass


def create_customer(user: User):
    customer = stripe.Customer.create(email=user.email)
    user.stripe_id = customer['id']
    db_commit()
    logging.info(f"Created stripe customer with id {customer['id']}")


def create_subscription(user: User, workspace: Workspace):
    products = stripe.Product.list()
    product_id_by_name = _get_product_id_by_name(products)
    workspace_product_id = product_id_by_name['Startup']
    prices = stripe.Price.list(product=workspace_product_id, limit=1)
    if prices['has_more']:
        raise MultiplePricesOfProductError(f"The product {workspace_product_id} has multiple prices,"
                                           f" we do not support that currently.")
    price = prices['data'][0]
    trial_end_date = datetime.utcnow() + timedelta(days=SUBSCRIPTION_TRIAL_DAYS)
    subscription = stripe.Subscription.create(
        customer=user.stripe_id,
        items=[{'price': price['id']}],
        trial_end=round(trial_end_date.timestamp())
    )
    workspace.subscription_end_date = trial_end_date
    workspace.stripe_subscription_id = subscription['id']
    db_commit()


def create_billing_info_update_session(user: User):
    session = stripe.checkout.Session.create(
        customer=user.stripe_id,
        payment_method_types=['card'],
        mode='setup',
        success_url='http://localhost:5000/',
        cancel_url='http://localhost:5000/',
    )
    return session


def _get_product_id_by_name(products):
    product_id_by_name = {}
    for p in products:
        product_id_by_name[p['name']] = p['id']
    return product_id_by_name
