from flask import current_app
from flask_socketio import emit


def send_update(event, data):
    """
    :param event: event name
    :param data: data to send to the socket
    """
    app = current_app._get_current_object()
    with app.app_context():
        emit(event, data, namespace='/socket', broadcast=True)
