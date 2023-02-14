"""
Controller functions of the water intake module
"""

import random
import threading
from typing import Union, Callable

from home_controller.io import MAIN_WATER_VALVE, WATER_FLOW_SENSOR, ELECTRICITY_SIGNAL, WATERING_ANY
from home_controller.config import (
    WATER_FLOW_SENSOR_MEASUREMENT_FREQUENCY,
    MAX_CONTINUOUS_WATER_FLOW_MINS,
    WFS_CONST_SUM,
    WFS_CONST_DIV,
)
from home_controller.utils import logging, pause, get_datetime

from .utils import save_flow_measurement  # , save_historical_consumption


def count_water_flow_sensor_pulse():
    '''
    Count water flow sensor pulses
    '''
    global WATER_FLOW_SENSOR_PULSES
    WATER_FLOW_SENSOR_PULSES += 1  # pylint: disable=undefined-variable


def measure_water_flow() -> float:
    '''
    Measure the water flow

    Args:
    - None

    Return:
    - Measured flow (float)
    '''
    global WATER_FLOW_SENSOR_PULSES
    global CONTINUOUS_WATER_FLOW_MINS

    flow = (
        (WATER_FLOW_SENSOR_PULSES * WATER_FLOW_SENSOR_MEASUREMENT_FREQUENCY) + WFS_CONST_SUM
    ) / WFS_CONST_DIV
    WATER_FLOW_SENSOR_PULSES = 0

    # Development purposes only
    flow = float(random.randint(0, 100))

    if flow != 0:
        CONTINUOUS_WATER_FLOW_MINS += (  # pylint: disable=undefined-variable
            1 / WATER_FLOW_SENSOR_MEASUREMENT_FREQUENCY
        ) / 60
    else:
        CONTINUOUS_WATER_FLOW_MINS = 0

    return flow


def automatic(func: Callable) -> Callable:
    '''
    Wraps a valve controller function to automatically open it or close it
    '''

    def automatic_control_main_water_valve():
        '''
        Determines if the valve controller wrapped function should be opened or closed
        based on some fixed rules which are checked on each iteration.

        Args:
        - None

        Return:
        - Wrapped function
        '''
        global CONTINUOUS_WATER_FLOW_MINS  # pylint: disable=global-variable-not-assigned

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


def control_main_water_valve(valve_open: Union[bool, None]) -> bool:
    '''
    Opens or close the main water valve and returns the current status.

    Args:
    - valve_open (bool, None): If the valve should be opened or closed.
        If None return the current status.

    Return:
    - Valve status (bool): True if open, False if close
    '''
    assert isinstance(valve_open, (bool, type(None)))

    if valve_open is not None:
        if valve_open:
            MAIN_WATER_VALVE.activate()
        else:
            MAIN_WATER_VALVE.deactivate()
    return MAIN_WATER_VALVE.status()


def water_flow_measurement_daemon():
    '''
    Measure the water which is flowing through the sensor

    Args:
    - None
    Return:
    - None
    '''
    # Configure the water sensor to detect failing pulses
    WATER_FLOW_SENSOR.add_event_detect(False, count_water_flow_sensor_pulse)

    while True:
        current_flow = measure_water_flow()
        current_dt = get_datetime(in_str=True)

        save_flow_measurement(current_dt, current_flow)

        # Opens or closes the main water valve depending on different parameters
        automatic(control_main_water_valve)()

        pause(1 / WATER_FLOW_SENSOR_MEASUREMENT_FREQUENCY)


# def historical_consumption_daemon():
#     '''

#     '''
#     while True:
#         save_historical_consumption()

#         pause(60 * 60 * 12)

# Keeps track of the pulses measured by the water flow sensor on each iteration
WATER_FLOW_SENSOR_PULSES: int = 0
# Keeps track of the time in minutes that the water has been flown through the sensor
CONTINUOUS_WATER_FLOW_MINS: float = 0

# Create a daemon thread to continuously measure the water flow
water_flow_measurement_thread = threading.Thread(
    name='water_flow_measurement_daemon', target=water_flow_measurement_daemon
)
water_flow_measurement_thread.daemon = True
water_flow_measurement_thread.start()

# # Create a daemon thread to aggregate water flow data
# historical_consumption_thread = threading.Thread(
#     name='historical_consumption_daemon',
#     target=historical_consumption_daemon
# )
# historical_consumption_thread.daemon = True
# historical_consumption_thread.start()
