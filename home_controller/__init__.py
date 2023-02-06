'''
Watering controller app
'''

from flask import Flask # pylint: disable=import-error
from flask_socketio import SocketIO # pylint: disable=import-error

app = Flask(__name__)
socketio = SocketIO(app, logger=False, engineio_logger=False, cors_allowed_origins='*')

from home_controller import routes
from home_controller import controller
