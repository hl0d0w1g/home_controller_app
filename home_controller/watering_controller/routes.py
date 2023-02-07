'''
Flask routes for the watering_controller
'''

from flask import render_template, request, jsonify # pylint: disable=import-error
# from flask_socketio import emit # pylint: disable=import-error

from home_controller import app, socketio
from home_controller.config import WATERING_NAMESPACE
from home_controller.utils import logging

from . import controller
from .utils import read_watering_config


# --- SOCKETS ---
@socketio.on('connect', namespace=WATERING_NAMESPACE)
def watering_controller_socket_connect():
    '''
    Socket connect event
    '''
    logging(
        'Web client connected',
        source='watering_controller/routes/socket_connect',
        source_module='watering_controller'
    )

@socketio.on('disconnect', namespace=WATERING_NAMESPACE)
def watering_controller_socket_disconnect():
    '''
    Socket disconnect event
    '''
    logging(
        'Web client disconnected',
        source='watering_controller/routes/socket_disconnect',
        source_module='watering_controller'
    )

# --- ROUTES ---
@app.route(WATERING_NAMESPACE)
def watering_controller_homepage():
    '''
    Watering controller main page
    '''
    return render_template('watering_controller.html')

@app.route(f'{WATERING_NAMESPACE}-edit-programs')
def watering_controller_edit_programs():
    '''
    Watering controller edit page programs
    '''
    return render_template('watering_controller_edit_programs.html')

@app.route('/programs', methods=['GET'])
def watering_controller_get_programs():
    '''
    Get all the programs
    '''
    return jsonify(read_watering_config())

@app.route('/programs', methods=['POST'])
def watering_controller_save_programs():
    '''
    Save the programs
    '''
    controller.new_programs_config(request.json)

    # if op_status:
    #     return ('{}', 200)

    # return ('[ERROR] Save operation was unsuccessful', 500)
    return ('{}', 200)

@app.route('/program/<idx>', methods=['GET'])
def watering_controller_init_program(idx:int):
    '''
    Initialize a program
    '''
    controller.init_program(int(idx))
    return ('{}', 200)

@app.route('/circuit/<idx>/<mins>', methods=['GET'])
def watering_controller_init_circuit(idx:int, mins:int):
    '''
    Initialize a circuit
    '''
    controller.init_circuit(int(idx), int(mins))
    return ('{}', 200)

@app.route('/cancel', methods=['GET'])
def watering_controller_stop_all():
    '''
    Stop all the programs
    '''
    controller.stop_watering()
    return ('{}', 200)
