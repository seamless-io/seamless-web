import os

from flask_socketio import SocketIO

from backend.web import create_app

app = create_app()
socketio = SocketIO(app, async_mode='threading')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=os.environ.get('PORT', 5000))
