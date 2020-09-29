import logging
import os

import stripe

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


def create_checkout_session(user: User, workspace: Workspace):
    products = stripe.Product.list()
    product_id_by_name = _get_product_id_by_name(products)
    # workspace_product_id = product_id_by_name[workspace.plan] TODO uncomment when workspace switching is implemented
    workspace_product_id = product_id_by_name['Startup']
    prices = stripe.Price.list(product=workspace_product_id, limit=1)
    if prices['has_more']:
        raise MultiplePricesOfProductError(f"The product {workspace_product_id} has multiple prices,"
                                           f" we do not support that currently.")
    price = prices['data'][0]
    session = stripe.checkout.Session.create(
        customer=user.stripe_id,
        payment_method_types=['card'],
        line_items=[{
            'price': price['id'],
            'quantity': 1,
        }],
        mode='subscription',
        success_url='http://localhost:5000/',
        cancel_url='http://localhost:5000/',
    )
    return session


def _get_product_id_by_name(products):
    product_id_by_name = {}
    for p in products:
        product_id_by_name[p['name']] = p['id']
    return product_id_by_name
