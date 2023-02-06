'''
Program class

An ordered list of circuits to activate during a certain time each circuit.
'''

from home_controller.utils import (
    logging, socket_emit, pause, hour_str_to_time, get_datetime, SPANISH_WEEKDAYS_SHORT
)

from .circuit import Circuit
from .config import WATERING_NAMESPACE, WATERING_N_CIRCUITS, WATERING_N_PROGRAMS
from .utils import read_watering_config


class Program():
    '''
    Program class
    '''

    def __init__(self, program:dict) -> None:
        '''
        Program class initialization

        Parameters
        ----------
        pins : dict
            Dictionary of circuits, where the key is the circuit id and the value
            is the actiavtion time in minutes.
            {circuit_id: activation_time_mins, ...}
        '''
        assert(isinstance(program, dict) and 0 <= len(program) <= WATERING_N_CIRCUITS)

        self.circuits = {
            Circuit(circuit_id): activation_time_mins \
                for circuit_id, activation_time_mins in program.items()
        }
        self.activated = False

    def __str__(self) -> str:
        '''
        Return a string representation of the program
        '''
        return f'Program circuits {self.circuits}'

    def __repr__(self) -> str:
        '''
        Return a string representation of the program
        '''
        return self.__str__()

    def execute(self, stop_event:bool=lambda: False) -> None:
        '''
        Execute program (sequence of circuits)
        '''
        self.activated = True

        for circuit, activation_time_mins in self.circuits.items():
            circuit.activate()

            logging(
                f'Initializing circuit {circuit.idx} for {activation_time_mins} minutes',
                source='watering_controller/program/execute',
                source_module='watering_controller'
            )

            segs = activation_time_mins * 60
            while segs > 0 and not stop_event():
                if segs % 60 == 0:
                    socket_emit(
                        'activated-circuits',
                        {'circuit': circuit.idx, 'activated': True, 'mins': activation_time_mins},
                        WATERING_NAMESPACE
                    )
                    # logging(
                    #     f'''Circuit {circuit.idx} activated,
                    #       {activation_time_mins} minutes remaining...''',
                    #     source='watering_controller/program/execute',
                    #     source_module='watering_controller'
                    # )

                    activation_time_mins -= 1
                pause(1)
                segs -= 1

            pause(1)
            circuit.deactivate()

            socket_emit(
                'activated-circuits',
                {'circuit': circuit.idx, 'activated': False, 'mins': 0},
                WATERING_NAMESPACE
            )
            logging(
                f'Circuit {circuit.idx} deactivated',
                source='watering_controller/program/execute',
                source_module='watering_controller'
            )

        self.activated = False


class ScheduledProgram(Program):
    '''
    Program to be executed by the watering_controller in a specific weekday and time.
    '''

    def __init__(self, program_id:int, weekday:str, hour:str) -> None:
        '''
        Initialize the ScheduledProgram
        '''
        assert(isinstance(program_id, int) and 1 <= program_id <= WATERING_N_PROGRAMS)
        assert(isinstance(weekday, str) and weekday in SPANISH_WEEKDAYS_SHORT)
        assert(isinstance(hour, str) and len(hour) == 5)

        self.program_id = program_id
        self.weekday = weekday
        self.hour = hour
        self.time = hour_str_to_time(hour)

        task_program_config = read_watering_config()[str(program_id)]['circuits']
        task_program_config = {
            int(circuit_id): int(circuit_info['time']) \
                for circuit_id, circuit_info in task_program_config.items() \
                    if circuit_info['activated']
        }

        super().__init__(task_program_config)

    def __str__(self) -> str:
        '''
        Return a string representation of the ScheduledProgram
        '''
        return f'Scheduled Program {self.program_id} at {self.weekday}/{self.hour}'

    def __repr__(self) -> str:
        '''
        Return a string representation of the ScheduledProgram
        '''
        return self.__str__()

    def check_schedule(self) -> bool:
        '''
        Check if the weekday and time of the scheduled program match the current weekday and time
        '''
        now = get_datetime()
        now_time = hour_str_to_time(f'{now.hour:02}:{now.minute:02}')
        now_weekday = list(SPANISH_WEEKDAYS_SHORT)[now.weekday()]

        schedule_weekday = self.weekday
        schedule_time = self.time

        return schedule_weekday == now_weekday and schedule_time == now_time

    def scheduled_execute(self, stop_event:bool=lambda: False) -> None:
        '''
        Execute scheduled program (sequence of circuits on the scheduled weekday and time)
        '''
        socket_emit(
            'activated-programs',
            {'program': self.program_id, 'activated': True},
            WATERING_NAMESPACE
        )

        logging(
            f'Initializing program {self.program_id}',
            source='watering_controller/program/scheduled_execute',
            source_module='watering_controller'
        )

        self.execute(stop_event)

        socket_emit(
            'activated-programs',
            {'program': self.program_id, 'activated': False},
            WATERING_NAMESPACE
        )

        logging(
            f'Program {self.program_id} finished',
            source='watering_controller/program/scheduled_execute',
            source_module='watering_controller'
        )
