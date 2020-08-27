import logging
import os

import sentry_sdk
from flask import session
from flask_socketio import SocketIO, join_room
from sentry_sdk.integrations.flask import FlaskIntegration

from config import SENTRY_DSN
from core.web import create_app

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[FlaskIntegration()]
)

# The name of this variable (as well as this file) is important for Beanstalk
application = create_app()

# Disable information logs from socketio, including PING/PONG logs
logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)
socketio = SocketIO(application, async_mode='threading')


@socketio.on('connect', namespace='/socket')
def connected():
    """https://stackoverflow.com/questions/39423646/flask-socketio-emit-to-specific-user"""

    logging.info(f"{session['profile']['email']} connected to the socket")
    join_room(session['profile']['internal_user_id'])


if __name__ == '__main__':
    socketio.run(application, host='0.0.0.0', port=os.environ.get('PORT', 5000))
