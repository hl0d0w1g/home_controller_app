"""
Configuration variables and constants for the whole app.
"""

####################################
#           RPI I/O Pins           #
####################################

# water_intake module
# ----------------------------------
# Raspberry Pi GPIO pin number for the water flow sensor
WATER_FLOW_SENSOR_PIN: int = 6
# Raspberry Pi GPIO pin number for the main water valve
MAIN_WATER_VALVE_PIN: int = 12
# Raspberry Pi GPIO pin number for the electricity signal
ELECTRICITY_SIGNAL_PIN: int = 13

# watering_controller module
# ----------------------------------
# Each circuit is represented by 4 pins (in binary) plus a
# 5th pin that is used to flag if any circuit is activated.
# MSB 0 bit numbering
WATERING_PIN_0: int = 20  # Most significant bit
WATERING_PIN_1: int = 26
WATERING_PIN_2: int = 16
WATERING_PIN_3: int = 19  # Least significant bit
WATERING_PIN_ANY: int = 21  # HIGH is used to flag if any circuit is activated, LOW otherwise


####################################
#            NAMESPACES            #
####################################

# water_intake module
# ----------------------------------
WATER_INTAKE_NAMESPACE: str = '/water-intake'

# watering_controller module
# ----------------------------------
WATERING_NAMESPACE: str = '/watering-controller'


####################################
#            CONSTANTS             #
####################################

# water_intake module
# ----------------------------------
# Water flow sensor constants for flow calc in L/m
WFS_CONST_SUM: float = 0
WFS_CONST_DIV: float = 7.5
# Frequency of water flow measurement per second (Hz)
WATER_FLOW_SENSOR_MEASUREMENT_FREQUENCY: float = 1 / 30
# Max time in minutes that the water could flow continuously
MAX_CONTINUOUS_WATER_FLOW_MINS: int = 120

# watering_controller module
# ----------------------------------
# Number of available programs
WATERING_N_PROGRAMS: int = 3
# Number of available circuits
WATERING_N_CIRCUITS: int = 12
