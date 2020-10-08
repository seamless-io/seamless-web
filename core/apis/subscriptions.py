from flask import Blueprint, request, jsonify, session, url_for, redirect, Response

from core.services import user as user_service
from core.services import subscription as subscription_service


subscription_bp = Blueprint('subscription', __name__)


@subscription_bp.route('/', methods=['POST'])
def checkout():
    user = user_service.get_by_id(session['profile']['internal_user_id'])
    checkout_success_url = url_for('subscription.success', _external=True)
    checkout_cancel_url = url_for('subscription.cancel', _external=True)
    if user.subscription:
        existing_subscription_id = user.subscription.id
    else:
        existing_subscription_id = None
    session_id = subscription_service.create_billing_update_session(user.customer_id, checkout_success_url,
                                                                    checkout_cancel_url, existing_subscription_id)
    print('SEssionID: ', session_id)
    return jsonify({'session_id': session_id})


@subscription_bp.route('/success')
def success():
    """
    On successful checkout
    """
    # TODO: pass a data about checkout success
    return redirect('/')


@subscription_bp.route('/cancel')
def cancel():
    """
    On failed checkout
    """
    # TODO: pass a data about checkout fail
    return redirect('/')


@subscription_bp.route('/webhook', methods=['POST'])
def webhook():
    try:
        is_success = subscription_service.process_event(request.data)
    except ValueError as exc:
        return Response(status=400)

    if is_success:
        return Response(status=200)
    else:
        return Response(status=500)



