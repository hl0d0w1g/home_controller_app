"""
Controller of water flow sensor
"""

import random
import threading

from home_controller.IO import (
    MAIN_WATER_VALVE, 
    WATER_FLOW_SENSOR, 
    ELECTRICITY_SIGNAL, 
    WATERING_ANY
)
from home_controller.config import (
    WATER_FLOW_SENSOR_MEASUREMENT_FREQUENCY, 
    MAX_CONTINUOUS_WATER_FLOW_MINS,
    WFS_CONST_SUM, 
    WFS_CONST_DIV
)
from home_controller.utils import logging, pause, get_datetime

from .utils import save_flow_measurement, save_historical_consumption


def count_water_flow_sensor_pulse(channel):
    '''
    Count sensor pulses
    '''
    global WATER_FLOW_SENSOR_PULSES
    WATER_FLOW_SENSOR_PULSES += 1


def measure_water_flow(gap:float) -> float:
    '''
    Measure the water flow
    '''
    global WATER_FLOW_SENSOR_PULSES
    global CONTINUOUS_WATER_FLOW_MINS

    flow = ((WATER_FLOW_SENSOR_PULSES * gap) + WFS_CONST_SUM) / WFS_CONST_DIV
    WATER_FLOW_SENSOR_PULSES = 0

    # Development purposes only
    flow = float(random.randint(0, 100))

    if flow != 0:
        CONTINUOUS_WATER_FLOW_MINS += (1 / WATER_FLOW_SENSOR_MEASUREMENT_FREQUENCY) / 60
    else:
        CONTINUOUS_WATER_FLOW_MINS = 0

    return flow

def automatic(func):

    def automatic_control_main_water_valve():
        global CONTINUOUS_WATER_FLOW_MINS

        electricity = ELECTRICITY_SIGNAL.read()
        watering = WATERING_ANY.status()
        if watering:
            valve_open = True
        elif electricity and CONTINUOUS_WATER_FLOW_MINS < MAX_CONTINUOUS_WATER_FLOW_MINS:
            valve_open = True
        else:
            valve_open = False

        func(valve_open)

    return automatic_control_main_water_valve

def control_main_water_valve(valve_open):
    '''
    
    '''
    if valve_open is not None:
        if valve_open:
            MAIN_WATER_VALVE.activate()
        else:
            MAIN_WATER_VALVE.deactivate()
    return MAIN_WATER_VALVE.status()
    

def water_flow_measurement_daemon():
    '''
    Keeps the control of the scheduled programs to be executed

    Args:
    - None

    Return:
    - None
    '''
    WATER_FLOW_SENSOR.add_event_detect(False, count_water_flow_sensor_pulse)

    while True:
        current_flow = measure_water_flow(WATER_FLOW_SENSOR_MEASUREMENT_FREQUENCY)
        current_dt = get_datetime(in_str=True)

        save_flow_measurement(current_dt, current_flow)

        automatic(control_main_water_valve)()

        pause(1 / WATER_FLOW_SENSOR_MEASUREMENT_FREQUENCY)

def historical_consumption_daemon():
    '''
    Keeps the control of the scheduled programs to be executed

    Args:
    - None

    Return:
    - None
    '''
    while True:
        save_historical_consumption()

        pause(60 * 60 * 12)

WATER_FLOW_SENSOR_PULSES:int = 0
CONTINUOUS_WATER_FLOW_MINS:float = 0

# Create a daemon thread to keep the control of the scheduled programs
water_flow_measurement_thread = threading.Thread(
    name='water_flow_measurement_daemon',
    target=water_flow_measurement_daemon
)
water_flow_measurement_thread.setDaemon(True)
water_flow_measurement_thread.start()

# # Create a daemon thread to keep the control of the scheduled programs
# historical_consumption_thread = threading.Thread(
#     name='historical_consumption_daemon',
#     target=historical_consumption_daemon
# )
# historical_consumption_thread.setDaemon(True)
# historical_consumption_thread.start()
