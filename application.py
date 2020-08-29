import logging
import os
from datetime import timedelta, datetime

import docker
import sentry_sdk
from dateutil.parser import parse
from flask import session
from flask_socketio import SocketIO, join_room
from sentry_sdk import capture_exception
from sentry_sdk.integrations.flask import FlaskIntegration
from timeloop import Timeloop

from config import SENTRY_DSN
from core.services.job import CONTAINER_NAME_PREFIX
from core.telegram.client import send_daily_stats
from core.web import create_app
from helpers import time_diff_in_seconds

JOB_EXECUTION_TIME_LIMIT_SECONDS = 30 * 60  # 30 minutes

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

tl = Timeloop()


@tl.job(interval=timedelta(seconds=60))
def kill_containers_over_time_limit():
    try:
        docker_client = docker.from_env()
        for container in docker_client.containers.list(filters={'status': 'running'}):
            if not container.name.startswith(CONTAINER_NAME_PREFIX):
                continue  # We only looking for containers that execute Jobs
            container_start_time = parse(container.attrs['State']['StartedAt'])
            running_time_seconds = time_diff_in_seconds(container_start_time.replace(tzinfo=None),
                                                        datetime.utcnow().replace(tzinfo=None))
            if running_time_seconds > JOB_EXECUTION_TIME_LIMIT_SECONDS:
                logging.info(f"Shutting down container {container.name} "
                             f"because it's running for {running_time_seconds} seconds")
                container.kill()
    except Exception as e:
        # We don't want the periodic task to shut down if some of its executions had an Exception
        logging.error(e)
        capture_exception(e)


@tl.job(interval=timedelta(hours=1))
def send_daily_stats_to_telegram():
    try:
        if datetime.utcnow().hour == 12:  # every day at 12:00 UTC
            send_daily_stats()
    except Exception as e:
        # We don't want the periodic task to shut down if some of its executions had an Exception
        logging.error(e)
        capture_exception(e)


@socketio.on('connect', namespace='/socket')
def connected():
    """https://stackoverflow.com/questions/39423646/flask-socketio-emit-to-specific-user"""

    logging.info(f"{session['profile']['email']} connected to the socket")
    join_room(session['profile']['internal_user_id'])


if __name__ == '__main__':
    tl.start()
    socketio.run(application, host='0.0.0.0', port=os.environ.get('PORT', 5000))
