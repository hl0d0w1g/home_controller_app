"""
Watering controller module web routes
"""

from flask import render_template, request, jsonify  # pylint: disable=import-error

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

    Args:
    - None
    Return:
    - None
    '''
    logging(
        'Web client connected',
        source_module='watering_controller',
        source_function='routes/socket_connect',
    )


@socketio.on('disconnect', namespace=WATERING_NAMESPACE)
def watering_controller_socket_disconnect():
    '''
    Socket disconnect event

    Args:
    - None
    Return:
    - None
    '''
    logging(
        'Web client disconnected',
        source_module='watering_controller',
        source_function='routes/socket_disconnect',
    )


# --- ROUTES ---
@app.route(WATERING_NAMESPACE)
def watering_controller_homepage():
    '''
    Watering controller module homepage

    Args:
    - None
    Return:
    - None
    '''
    return render_template('watering_controller.html')


@app.route(f'{WATERING_NAMESPACE}/edit-programs')
def watering_controller_edit_programs():
    '''
    Watering controller edit programs page

    Args:
    - None
    Return:
    - None
    '''
    return render_template('watering_controller_edit_programs.html')


@app.route(f'{WATERING_NAMESPACE}/programs', methods=['GET'])
def watering_controller_get_programs():
    '''
    Get all the programs

    Args:
    - None
    Return:
    - None
    '''
    return jsonify(read_watering_config())


@app.route(f'{WATERING_NAMESPACE}/programs', methods=['POST'])
def watering_controller_save_programs():
    '''
    Save programs

    Args:
    - None
    Return:
    - None
    '''
    controller.new_scheduled_programs_config(request.json)
    return ('{}', 200)


@app.route(f'{WATERING_NAMESPACE}/program/<idx>', methods=['GET'])
def watering_controller_init_program(idx: int):
    '''
    Initialize a program

    Args:
    - idx (int): Identifier of the program to initialize

    Return:
    - None
    '''
    controller.init_program(int(idx))
    return ('{}', 200)


@app.route(f'{WATERING_NAMESPACE}/circuit/<idx>/<mins>', methods=['GET'])
def watering_controller_init_circuit(idx: int, mins: int):
    '''
    Initialize a circuit

    Args:
    - idx (int): Identifier of the circuit to initialize
    - mins (int): Minutes during which the circuit wil be open

    Return:
    - None
    '''
    controller.init_circuit(int(idx), int(mins))
    return ('{}', 200)


@app.route(f'{WATERING_NAMESPACE}/cancel', methods=['GET'])
def watering_controller_stop_all():
    '''
    Deactivate all the programs and circuits

    Args:
    - None
    Return:
    - None
    '''
    controller.stop_watering()
    return ('{}', 200)
