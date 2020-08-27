from flask_socketio import emit


def send_update(event, data, user_id):
    """
    :param user_id: the database id of the User who is the receiver of socket events
    :param event: event name
    :param data: data to send to the socket
    https://stackoverflow.com/questions/39423646/flask-socketio-emit-to-specific-user
    """
    emit(event, data, namespace='/socket', room=user_id)
