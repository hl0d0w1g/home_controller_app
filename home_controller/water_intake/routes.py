"""
Water intake module web routes
"""

from flask import render_template, request, jsonify # pylint: disable=import-error

from home_controller import app #, socketio
from home_controller.config import WATER_INTAKE_NAMESPACE
from home_controller.utils import logging

from . import controller
from .utils import read_flow_measurement#, read_historical_consumption

# # --- SOCKETS ---
# @socketio.on('connect', namespace=WATER_INTAKE_NAMESPACE)
# def water_intake_socket_connect():
#     '''
#     Socket connect event
#     '''
#     logging(
#         'Web client connected',
#         source_module='water_intake',
#         source_function='routes/socket_connect'
#     )

# @socketio.on('disconnect', namespace=WATER_INTAKE_NAMESPACE)
# def water_intake_socket_disconnect():
#     '''
#     Socket disconnect event
#     '''
#     logging(
#         'Web client disconnected',
#         source_module='water_intake',
#         source_function='routes/socket_disconnect'
#     )

# --- ROUTES ---
@app.route(WATER_INTAKE_NAMESPACE)
def water_intake_homepage():
    '''
    Water intake homepage
    
    Args:
    - None
    Return:
    - None
    '''
    return render_template('water_intake.html')

@app.route(f'{WATER_INTAKE_NAMESPACE}/flow-sensor-data', methods=['GET'])
def water_intake_get_flow_sensor_data():
    '''
    Get the water flow measured by the sensor

    Args:
    - None
    Return:
    - None
    '''
    n_data_points = request.args.get('data-points', default=1, type=int)
    return jsonify(read_flow_measurement(n_data_points))

# @app.route(f'{WATER_INTAKE_NAMESPACE}/historical-consumption-data', methods=['GET'])
# def water_intake_get_historical_consumption_data():
#     '''
#     Get the water consumption (aggregate flow data)

#     Args:
#     - None
#     Return:
#     - None
#     '''
#     period = request.args.get('period', default=1, type=str)
#     return jsonify(read_historical_consumption(period))

@app.route(f'{WATER_INTAKE_NAMESPACE}/main-water-valve', methods=['GET'])
def water_intake_main_water_valve():
    '''
    Control the main water valve status by a query param

    Args:
    - None
    Return:
    - None
    '''
    valve_status = request.args.get('status', default='', type=str)
    valve_status = None if not valve_status else valve_status == 'true'
    valve_status = controller.control_main_water_valve(valve_status)
    return str(valve_status).lower()
