"""
Raspberry Pi pin classes and methods for Input/Output pins 
"""

from typing import Callable, Any
from RPi import GPIO # pylint: disable=import-error
# from home_controller import utils

# Number of BCM pins on a Raspberry Pi 4
N_PINS:int = 27

GPIO.setmode(GPIO.BCM)


class RpiPinIn():
    '''
    Raspberry Pi pin class to configure INPUT pins
    '''

    def __init__(self, pin:int, pull_up_down:bool=False):
        '''
        Initialize RpiPinIn class
                
        Args:
        - pin (int): Pin number in BCM mode to be configured
        - pull_up_down (bool): Pull up (True) or pull down (False) resistance
        '''
        assert(isinstance(pin, int) and 1 <= pin <= N_PINS), \
            'Provide an integer pin number between 1 and ' + str(N_PINS)
        assert isinstance(pull_up_down, bool)

        self.pin = pin

        # PULL_UP=True PULL_DOWN=False
        self.pull_up_down = GPIO.PUD_UP if pull_up_down else GPIO.PUD_DOWN
        self.event_detect_mode = None

        GPIO.setup(self.pin, GPIO.IN, self.pull_up_down)

    def __str__(self) -> str:
        '''
        Return a string representation of the pin
                
        Args:
        - None
        Return:
        - String representation of the pin
        '''
        return f'''
                RPI pin {self.pin} configured as INPUT, 
                (BCM board mode)
                '''

    def __repr__(self) -> str:
        '''
        Return a string representation of the pin
                
        Args:
        - None
        Return:
        - String representation of the pin
        '''
        return self.__str__()

    def read(self) -> Any:
        '''
        Reading the input of the pin

        Args:
        - None
        Return:
        - Pin value (Any)
        '''
        return GPIO.input(self.pin)

    def add_event_detect(self, mode:bool, callback:Callable) -> None:
        '''
        Add a function to be executed when an event occurs in the pin

        Args:
        - mode (bool): If the callback should be triggered on rising (True) of falling (False)
        - callback (Callable): Function to be called when the event is detected

        Return:
        - None
        '''
        self.event_detect_mode = GPIO.RISING if mode else GPIO.FALLING
        GPIO.add_event_detect(self.pin, self.event_detect_mode, callback=callback)


class RpiPinOut():
    '''
    Raspberry Pi pin class to configure INPUT pins
    '''

    def __init__(self, pin:int, initial:bool=False):
        '''
        Initialize RpiPinOut class
                
        Args:
        - pin (int): Pin number in BCM mode to be configured
        - initial (bool): Initial value, True for HIGH, False for LOW
        '''
        assert(isinstance(pin, int) and 1 <= pin <= N_PINS), \
            'Provide an integer pin number between 1 and ' + str(N_PINS)
        assert isinstance(initial, bool)

        self.pin = pin
        self.activated = GPIO.HIGH if initial else GPIO.LOW

        GPIO.setup(self.pin, GPIO.OUT, initial=self.activated)

    def __str__(self) -> str:
        '''
        Return a string representation of the pin
                
        Args:
        - None
        Return:
        - None
        '''
        return f'''
                RPI pin {self.pin} configured as OUTPUT, 
                is activated: {self.activated} (BCM board mode)
                '''

    def __repr__(self) -> str:
        '''
        Return a string representation of the pin
                
        Args:
        - None
        Return:
        - None
        '''
        return self.__str__()

    def status(self) -> bool:
        '''
        Return if the pin is activated or not
                
        Args:
        - None
        Return:
        - None
        '''
        return True if self.activated == GPIO.HIGH else False

    def activate(self) -> None:
        '''
        Activate pin, by setting pin to HIGH
                
        Args:
        - None
        Return:
        - None
        '''
        self.activated = GPIO.HIGH
        GPIO.output(self.pin, self.activated)

        # utils.logging(
        #     f'RPI pin {self.pin} activated',
        #     source_module='home_controller',
        #     source_function='rpi_pin/activate'
        #     )

    def deactivate(self) -> None:
        '''
        Deactivate pin, by setting pin to LOW
                
        Args:
        - None
        Return:
        - None
        '''
        self.activated = GPIO.LOW
        GPIO.output(self.pin, self.activated)

        # utils.logging(
        #     f'RPI pin {self.pin} deactivated',
        #     source_module='home_controller',
        #     source_function='rpi_pin/deactivate'
        #     )
