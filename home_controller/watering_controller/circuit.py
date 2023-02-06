"""
Circuit

Set of rpi pins to activate or deactivate a watering circuit.
"""

from home_controller.rpi_pin import RpiPin
from home_controller.utils import logging

from .config import (
    WATERING_N_CIRCUITS, WATERING_PIN_ANY, WATERING_PIN_0,
    WATERING_PIN_1, WATERING_PIN_2, WATERING_PIN_3
)


class Circuit():
    """
    Circuit class
    """

    def __init__(self, idx:int) -> None:
        """
        Circuit class initialization

        Parameters
        ----------
        pins : dict
            Dictionary of pins, where the key is the pin id and the value is the pin activation.
            {
                pin1: active_pin1,
                pin2: active_pin2,
                pin3: active_pin3,
                pin4: active_pin4,
                pin_any: active_pin_any
            }

            Circuits are coded in binary, so each circuit is represented by 4 pins plus a 5th pin
            that is used to flag if any circuit is activated.
        """
        assert(isinstance(idx, int) and 1 <= idx <= WATERING_N_CIRCUITS)

        self.idx = idx
        self.pins = {
            RpiPin(pin, True): active \
                for pin, active in self.__circuit_activation_mask__(idx).items()
        }
        self.activated = False

    def __circuit_activation_mask__(self, idx:int) -> dict:
        '''
        Calculate the activation mask for the circuit

        Returns
        ----------
        dict
            Dictionary of pins, where the key is the pin id and the value is the pin activation.
            {
                pin1: active_pin1,
                pin2: active_pin2,
                pin3: active_pin3,
                pin4: active_pin4,pin_any: active_pin_any
            }

            Circuits are coded in binary, so each circuit is represented by 4 pins plus a 5th pin
            that is used to flag if any circuit is activated.
        '''
        watering_pins = {
            3: WATERING_PIN_3,
            2: WATERING_PIN_2,
            1: WATERING_PIN_1,
            0: WATERING_PIN_0,
            'any': WATERING_PIN_ANY
        }

        active_mask = [bool(int(b)) for b in f'{idx:04b}']
        pins = {
            pin: active_mask[int(b)] if b != 'any' else True \
                for b, pin in watering_pins.items()
        }
        return pins

    def __str__(self) -> str:
        """
        Return a string representation of the circuit
        """
        return f'Circuit (activated: {self.activated}) on {self.pins}'

    def __repr__(self) -> str:
        """
        Return a string representation of the circuit
        """
        return self.__str__()

    def activate(self) -> None:
        """
        Activate circuit, by setting circuit pins to HIGH, otherwise LOW
        """
        for pin, active in self.pins.items():
            if active:
                pin.activate()
            else:
                pin.deactivate()

        self.activated = True
        logging(
            f'circuit {self.idx} activated',
            source='watering_controller/circuit/activate',
            source_module='watering_controller'
        )

    def deactivate(self) -> None:
        """
        Deactivate circuit, by setting all pins to LOW
        """
        for pin, _ in self.pins.items():
            pin.deactivate()

        self.activated = False
        logging(
            f'circuit {self.idx} deactivated',
            source='watering_controller/circuit/deactivate',
            source_module='watering_controller'
        )
