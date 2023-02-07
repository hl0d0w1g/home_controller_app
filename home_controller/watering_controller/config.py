'''
Configuration file for the watering_controller.
'''

# # Namespace of the webapp for the watering_controller module
# WATERING_NAMESPACE:str = '/watering-controller'

# # Number of programs
# WATERING_N_PROGRAMS:int = 3

# # Number of circuits
# WATERING_N_CIRCUITS:int = 12

# # Raspberry Pi 4 BCM pins to use for the circuits.
# # Each circuit is represented by 4 pins (in binary) plus a
# # 5th pin that is used to flag if any circuit is activated.
# # MSB 0 bit numbering
# WATERING_PIN_0:int = 20 # Most significant bit
# WATERING_PIN_1:int = 26
# WATERING_PIN_2:int = 16
# WATERING_PIN_3:int = 19 # Least significant bit
# WATERING_PIN_ANY:int = 21 # HIGH is used to flag if any circuit is activated, LOW otherwise
