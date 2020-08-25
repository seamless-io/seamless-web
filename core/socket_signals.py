from flask_socketio import emit


def send_update(event, data):
    """
    :param event: event name
    :param data: data to send to the socket
    """
    emit(event, data, namespace='/socket', broadcast=True)
