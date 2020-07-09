import os

from flask_socketio import SocketIO

from backend.web import create_app

# The name of this variable (as well as this file) is important for Beanstalk
application = create_app()
socketio = SocketIO(application, async_mode='threading')

if __name__ == '__main__':
    socketio.run(application, host='0.0.0.0', port=os.environ.get('PORT', 5000))
