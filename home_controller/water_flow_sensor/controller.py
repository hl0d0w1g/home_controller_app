"""
Controller of water flow sensor
"""

import random
import threading

from home_controller.rpi_pin import RpiPin

from .config import WATER_FLOW_SENSOR_MEASUREMENT_FREQUENCY, MAIN_WATER_VALVE_PIN
from .utils import save_flow_measurement, save_historical_consumption

from home_controller.utils import logging, pause, get_datetime


def measure_water_flow(gap:float) -> float:
    '''
    Measure the water flow
    '''
    flow = 0.0

    flow = ((counts * gap) / 7.5)
    counts = 0
    # import RPi.GPIO as GPIO
    # import time, sys
    
    # FLOW_SENSOR_GPIO = 2
    
    # GPIO.setmode(GPIO.BCM)
    # GPIO.setup(FLOW_SENSOR_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    
    # global count
    # count = 0
    
    # def countPulse(channel):
    # global count
    # if start_counter == 1:
    #     count = count+1
    
    # GPIO.add_event_detect(FLOW_SENSOR_GPIO, GPIO.FALLING, callback=countPulse)
    
    # while True:
    #         start_counter = 1
    #         time.sleep(1)
    #         start_counter = 0
    # (F + 4) / 8 = Q
    # flow = (count + 4) / 8
    #         flow = (count / 7.5) # Pulse frequency (Hz) = 7.5Q, Q is flow rate in L/min.
    #         print("The flow is: %.3f Liter/min" % (flow))
    #         count = 0
    #         time.sleep(0.1)

    return flow

# def measure_water_flow() -> int:
#     '''
#     Measure the water flow
#     '''
#     return random.randint(0, 100)


def control_main_water_valve(valve_status:bool) -> bool:
    '''
    Measure the water flow
    '''
    main_water_valve = RpiPin(MAIN_WATER_VALVE_PIN, True)

    if valve_status:
        main_water_valve.activate()
    return valve_status

def water_flow_measurement_daemon():
    '''
    Keeps the control of the scheduled programs to be executed

    Args:
    - None

    Return:
    - None
    '''
    while True:
        current_flow = measure_water_flow(WATER_FLOW_SENSOR_MEASUREMENT_FREQUENCY)
        current_dt = get_datetime(in_str=True)

        save_flow_measurement(current_dt, current_flow)

        # control_main_water_valve(current_flow)

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
