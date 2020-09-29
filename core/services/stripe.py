import logging
import os

import stripe

from core.models import User, db_commit

# Set your secret key. Remember to switch to your live secret key in production!
# See your keys here: https://dashboard.stripe.com/account/apikeys
stripe.api_key = os.getenv('STRIPE_API_KEY')


def create_customer(user: User):
    customer = stripe.Customer.create(email=user.email)
    user.stripe_id = customer['id']
    db_commit()
    logging.info(f"Created stripe customer with id {customer['id']}")
