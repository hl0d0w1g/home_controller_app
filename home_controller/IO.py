"""
Input/Output variables for the whole app
"""

from home_controller.rpi_pin import RpiPinIn, RpiPinOut
from home_controller.config import (
    MAIN_WATER_VALVE_PIN,
    WATER_FLOW_SENSOR_PIN,
    ELECTRICITY_SIGNAL_PIN,
    WATERING_PIN_0,
    WATERING_PIN_1,
    WATERING_PIN_2,
    WATERING_PIN_3,
    WATERING_PIN_ANY,
)

# water_intake module
# ----------------------------------
MAIN_WATER_VALVE = RpiPinOut(MAIN_WATER_VALVE_PIN)
WATER_FLOW_SENSOR = RpiPinIn(WATER_FLOW_SENSOR_PIN, True)
ELECTRICITY_SIGNAL = RpiPinIn(ELECTRICITY_SIGNAL_PIN)

# watering_controller module
# ----------------------------------
# Each circuit is represented by 4 pins (in binary) plus a
# 5th pin that is used to flag if any circuit is activated.
# MSB 0 bit numbering
WATERING_0 = RpiPinOut(WATERING_PIN_0)
WATERING_1 = RpiPinOut(WATERING_PIN_1)
WATERING_2 = RpiPinOut(WATERING_PIN_2)
WATERING_3 = RpiPinOut(WATERING_PIN_3)
WATERING_ANY = RpiPinOut(WATERING_PIN_ANY)
