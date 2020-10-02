import logging
import os

from sqlalchemy.orm.exc import NoResultFound

from core.api_key import generate_api_key
from core.emails.client import send_welcome_email
from core.models import db_commit
from core.models.subscriptions import SubscriptionName
from core.models.users import User
from core.telegram.client import notify_about_new_user
from core.web import get_db_session
import core.services.subscription as subscription_service
import core.services.workspace as workspace_service
import core.services.plan as plan_service


class UserNotFoundException(Exception):
    pass


class UserAlreadyExists(Exception):
    pass


def get_by_api_key(api_key: str):
    try:
        user = User.get_user_from_api_key(api_key, get_db_session())
    except NoResultFound:
        raise UserNotFoundException('API Key is wrong, please go to our account https://app.seamlesscloud.io/account,'
                                    ' copy the API Key field and run "smls init <api key>"')
    return user


def get_by_id(user_id: str):
    try:
        user = User.get_user_from_id(user_id, get_db_session())
    except NoResultFound:
        raise UserNotFoundException(f'Cannot find a user with id: {user_id}')
    return user


def _create(email: str):
    user = User(email=email,
                api_key=generate_api_key())
    db_session = get_db_session()
    db_session.add(user)
    db_commit()
    return user


def sign_up(email, subscription_name=SubscriptionName.Personal.value):
    """
    Creates a user record in the database all necessary records according to the pricing plan
    """
    try:
        existing_user = User.get_user_from_email(email, get_db_session())
    except NoResultFound:
        existing_user = False

    if existing_user:
        raise UserAlreadyExists(f'The user {email} already exists in the database')

    user = _create(email)
    user_id = str(user.id)
    # We create Personal workspace for all accounts disregarding of the chosen plan
    personal_workspace_id = workspace_service.create_workspace(str(user_id), SubscriptionName.Personal.value).id
    workspace_service.add_user_to_workspace(user_id, personal_workspace_id)

    paid_workspace_id = None
    if subscription_name != SubscriptionName.Personal.value:
        paid_workspace = workspace_service.create_workspace(str(user_id), subscription_name)
        paid_workspace_id = str(paid_workspace.id)
        workspace_service.add_user_to_workspace(user_id, paid_workspace_id)
        subscription_service.create_customer(user)
        subscription = subscription_service.create_subscription(user)
        plan_service.create_workspace_plan(subscription, paid_workspace)

    logging.info(f"Created user {user_id}, with personal workspace {personal_workspace_id} "
                 f"{'' if not paid_workspace_id else f'and {subscription_name} workspace {paid_workspace_id}'}")
    if os.getenv('STAGE', 'local') == 'prod':
        notify_about_new_user(email, subscription_name)
        send_welcome_email(email)

    return user_id
