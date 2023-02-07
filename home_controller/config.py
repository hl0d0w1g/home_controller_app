"""

"""

####################################
#           RPI I/O Pins           #
#     Namespace of the webapp      #
####################################

# water_flow_sensor module
# ----------------------------------
# Raspberry Pi GPIO pin number for the water flow sensor
WATER_FLOW_SENSOR_PIN:int = 4
# Raspberry Pi GPIO pin number for the main water valve
MAIN_WATER_VALVE_PIN:int = 5
# Raspberry Pi GPIO pin number for the electricity signal
ELECTRICITY_SIGNAL_PIN:int = 6

# watering_controller module
# ----------------------------------
# Each circuit is represented by 4 pins (in binary) plus a
# 5th pin that is used to flag if any circuit is activated.
# MSB 0 bit numbering
WATERING_PIN_0:int = 20 # Most significant bit
WATERING_PIN_1:int = 26
WATERING_PIN_2:int = 16
WATERING_PIN_3:int = 19 # Least significant bit
WATERING_PIN_ANY:int = 21 # HIGH is used to flag if any circuit is activated, LOW otherwise


####################################
#            NAMESPACES            #
####################################

# water_flow_sensor module
# ----------------------------------
WATER_FLOW_SENSOR_NAMESPACE:str = '/water-flow-sensor'

# watering_controller module
# ----------------------------------
WATERING_NAMESPACE:str = '/watering-controller'


####################################
#            CONSTANTS             #
####################################

# water_flow_sensor module
# ----------------------------------
# Water flow sensor constants for flow calc in L/m
WFS_CONST_SUM:float = 0 #8
WFS_CONST_DIV:float = 7.5 #6
# Measure the water flow per second (Hz)
WATER_FLOW_SENSOR_MEASUREMENT_FREQUENCY:float = 1 / 30

# watering_controller module
# ----------------------------------
# Number of programs
WATERING_N_PROGRAMS:int = 3
# Number of circuits
WATERING_N_CIRCUITS:int = 12
