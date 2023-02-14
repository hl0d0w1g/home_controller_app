"""
Circuit

Set of rpi pins to activate or deactivate a watering circuit.
"""

from home_controller.config import WATERING_N_CIRCUITS
from home_controller.io import WATERING_0, WATERING_1, WATERING_2, WATERING_3, WATERING_ANY
from home_controller.utils import logging


class Circuit():
    '''
    Circuit class to configure RPi pins within circuit
    '''

    def __init__(self, idx:int):
        '''
        Circuit class initialization

        Args:
        - idx (int): Id of the circuit to be setup
        '''
        assert(isinstance(idx, int) and 1 <= idx <= WATERING_N_CIRCUITS), \
            'Provide an integer circuit id between 1 and ' + str(WATERING_N_CIRCUITS)

        self.idx = idx
        self.pins = self.__circuit_activation_mask__(idx)
        self.activated = False

    def __str__(self) -> str:
        '''
        Return a string representation of the circuit
                
        Args:
        - None
        Return:
        - String representation of the circuit
        '''
        return f'Circuit (activated: {self.activated}) on {self.pins}'

    def __repr__(self) -> str:
        '''
        Return a string representation of the circuit
                
        Args:
        - None
        Return:
        - String representation of the circuit
        '''
        return self.__str__()

    def __circuit_activation_mask__(self, idx:int) -> dict:
        '''
        Calculate the activation mask for the circuit

        Args:
        - idx (int):
        Return:
        - Dictionary of pins (dict), where the key is the pin (RpiPin type) 
          and the value is the pin activation.
            {
                pin1: active_pin1,
                pin2: active_pin2,
                pin3: active_pin3,
                pin4: active_pin4,
                pin_any: active_pin_any
            }

            Circuits are coded in binary, so each circuit is represented by 4 pins plus a 5th pin
            that is used to flag if any circuit is activated.
        '''
        watering_pins = {
            3: WATERING_3,
            2: WATERING_2,
            1: WATERING_1,
            0: WATERING_0,
            'any': WATERING_ANY
        }

        active_mask = [bool(int(b)) for b in f'{idx:04b}']
        pins = {
            pin: active_mask[int(b)] if b != 'any' else True \
                for b, pin in watering_pins.items()
        }
        return pins

    def activate(self) -> None:
        '''
        Activate circuit, by setting circuit pins to HIGH, otherwise LOW
                
        Args:
        - None
        Return:
        - None
        '''
        for pin, active in self.pins.items():
            if active:
                pin.activate()
            else:
                pin.deactivate()

        self.activated = True
        logging(
            f'circuit {self.idx} activated',
            source_module='watering_controller',
            source_function='circuit/activate'
        )

    def deactivate(self) -> None:
        '''
        Deactivate circuit, by setting all pins to LOW
                
        Args:
        - None
        Return:
        - None
        '''
        for pin, _ in self.pins.items():
            pin.deactivate()

        self.activated = False
        logging(
            f'circuit {self.idx} deactivated',
            source_module='watering_controller',
            source_function='circuit/deactivate'
        )
