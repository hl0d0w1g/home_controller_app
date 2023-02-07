'''
Flask routes for the watering_controller
'''

from flask import render_template, request, jsonify # pylint: disable=import-error
# from flask_socketio import emit # pylint: disable=import-error

from home_controller import app #, socketio
from home_controller.config import WATER_FLOW_SENSOR_NAMESPACE
from home_controller.utils import logging

from . import controller
from .utils import read_flow_measurement, read_historical_consumption

# # --- SOCKETS ---
# @socketio.on('connect', namespace=WATER_FLOW_SENSOR_NAMESPACE)
# def water_flow_sensor_socket_connect():
#     '''
#     Socket connect event
#     '''
#     logging(
#         'Web client connected',
#         source='water_flow_sensor/routes/socket_connect',
#         source_module='watering_controller'
#     )

# @socketio.on('disconnect', namespace=WATER_FLOW_SENSOR_NAMESPACE)
# def water_flow_sensor_socket_disconnect():
#     '''
#     Socket disconnect event
#     '''
#     logging(
#         'Web client disconnected',
#         source='water_flow_sensor/routes/socket_disconnect',
#         source_module='watering_controller'
#     )

# --- ROUTES ---
@app.route(WATER_FLOW_SENSOR_NAMESPACE)
def water_flow_sensor_homepage():
    '''
    Watering controller main page
    '''
    return render_template('water_flow_sensor.html')

@app.route('/flow-sensor-data', methods=['GET'])
def water_flow_sensor_get_flow_sensor_data():
    '''
    Get all the programs
    '''
    n_data_points = request.args.get('data-points', default=1, type=int)
    return jsonify(read_flow_measurement(n_data_points))

@app.route('/historical-consumption-data', methods=['GET'])
def water_flow_sensor_get_historical_consumption_data():
    '''
    Get all the programs
    '''
    period = request.args.get('period', default=1, type=str)
    return jsonify(read_historical_consumption(period))

@app.route('/main-water-valve', methods=['GET'])
def water_flow_sensor_main_water_valve():
    '''
    Get all the programs
    '''

    valve_status = request.args.get('status', default='', type=str)
    valve_status = None if not valve_status else True if valve_status == 'true' else False
    valve_status = controller.control_main_water_valve(valve_status)

    return str(valve_status).lower()
