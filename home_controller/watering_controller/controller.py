'''
Controller functions
'''

import threading
import signal

from home_controller.rpi_pin import RpiPin
from home_controller.utils import logging, socket_emit, get_datetime, pause

from .program import Program, ScheduledProgram
from .utils import save_watering_config, read_watering_config, weekday_time_combinations
from .config import (
    WATERING_N_CIRCUITS, WATERING_PIN_ANY, WATERING_PIN_0,
    WATERING_PIN_1, WATERING_PIN_2, WATERING_PIN_3,
    WATERING_N_PROGRAMS, WATERING_NAMESPACE
)


def init_program(idx:int) -> None:
    '''
    Init program
    '''
    assert(isinstance(idx, int) and 1 <= idx <= WATERING_N_PROGRAMS)

    resume_watering()

    program = ScheduledProgram(idx, 'L', '00:00')
    threading.Thread(target=program.execute, args=(is_watering_stopped,)).start()

def init_circuit(idx:int, mins:int) -> None:
    '''
    Execute the circuit by the indicated mins
    '''
    assert(isinstance(idx, int) and 1 <= idx <= WATERING_N_CIRCUITS)
    assert(isinstance(mins, int) and mins >= 0)

    resume_watering()

    # Create a program of only one circuit
    circuit_program = Program({idx: mins})
    threading.Thread(target=circuit_program.execute, args=(is_watering_stopped,)).start()

def close_all_circuits() -> None:
    '''
    Close all circuits setting all pins to LOW

    Args:
    - None

    Return:
    - None
    '''
    logging(
        'Deactivating all',
        source='watering_controller/controller/close_all_circuits',
        source_module='watering_controller'
    )
    watering_pins = [
        WATERING_PIN_3,
        WATERING_PIN_2,
        WATERING_PIN_1,
        WATERING_PIN_0,
        WATERING_PIN_ANY
    ]

    for pin in watering_pins:
        logging(
            f'Pin {pin} deactivated',
            source='watering_controller/controller/close_all_circuits',
            source_module='watering_controller'
        )
        RpiPin(pin, True).deactivate()

def new_programs_config(config:dict) -> None:
    '''
    Update the list of programs
    '''
    scheduled_programs = create_scheduled_programs(config)
    update_scheduled_programs(scheduled_programs)

    save_watering_config(config)

def create_scheduled_programs(config:dict) -> list:
    '''
    Create a the list of scheduled_programs

    Args:
    - config (dict): Watering configuration dictionary

    Return:
    - scheduled_programs (list(ScheduledProgram)): List of ScheduledProgram objects
    '''
    assert isinstance(config, dict)

    scheduled_programs_ls = []
    for program_id, program_info in config.items():
        if program_info['selected']:
            program_days = [day for day, activated in program_info['days'].items() if activated]
            program_starts = [
                start_info['hour'] for start_id, start_info in program_info['starts'].items() \
                    if start_info['activated']
            ]
            scheduled_programs = weekday_time_combinations(program_days, program_starts)
            scheduled_programs = [
                ScheduledProgram(int(program_id), day, hour) \
                    for (day, hour) in scheduled_programs if day and hour
            ]
            scheduled_programs_ls += scheduled_programs

    logging(
        f'Creating scheduled_programs: {scheduled_programs_ls}',
        source='watering_controller/controller/create_scheduled_programs',
        source_module='watering_controller'
    )

    return scheduled_programs_ls

# def check_scheduled_programs(scheduled_programs:list) -> int:
#     '''
#     Check if any task needs to be executed

#     Args:
#     - scheduled_programs (list(ScheduledProgram)): List of ScheduledProgram objects

#     Return:
#     - task_idx (int): Index of the ScheduledProgram object to be executed
#     '''
#     assert isinstance(scheduled_programs, list)

#     task_idx = None

#     for idx, task in enumerate(scheduled_programs):
#         if task.check_schedule():
#             task_idx = idx
#             break

#     return task_idx

def update_scheduled_programs(new_scheduled_programs:list) -> None:
    '''
    Update the list of scheduled_programs

    Args:
    - new_scheduled_programs (list): List of tuples with the new scheduled_programs

    Return:
    - None
    '''
    global SCHEDULED_PROGRAMS
    SCHEDULED_PROGRAMS = new_scheduled_programs

def scheduled_programs_daemon():
    '''
    Keeps the control of the scheduled programs to be executed

    Args:
    - None

    Return:
    - None
    '''
    global SCHEDULED_PROGRAMS #, STOP_WATERING
    config = read_watering_config()
    SCHEDULED_PROGRAMS = create_scheduled_programs(config)

    while True:
        program_to_execute = next((p for p in SCHEDULED_PROGRAMS if p.check_schedule()), None)
        if program_to_execute is not None:
            # task = SCHEDULED_PROGRAMS[task_to_execute]
            # task_to_execute.execute()
            logging(
                f'Executing Program: {program_to_execute}',
                source='watering_controller/controller/scheduled_programs_daemon',
                source_module='watering_controller'
            )
            threading.Thread(target=program_to_execute.execute, args=(is_watering_stopped,)).start()
            pause(60)
        else:
            pause(15)

        # if STOP_WATERING:
        #     pause(60)
        #     resume_watering()
        # else:
        #     pause(15)

def is_watering_stopped() -> bool:
    '''
    Return True if the watering should be stopped, False otherwise
    '''
    return STOP_WATERING

def stop_watering() -> None:
    '''
    Cancel all the current programs and circuits activations

    Args:
    - None

    Return:
    - None
    '''
    global STOP_WATERING
    STOP_WATERING = True

    socket_emit('cancell-all', {}, WATERING_NAMESPACE)

def resume_watering() -> None:
    '''
    Set to false the cancel flag

    Args:
    - None:

    Return:
    - None
    '''
    global STOP_WATERING
    STOP_WATERING = False

def gracefully_stop(signal_number, frame):
    '''
    Managing signals to close all circuits before continue
    '''
    logging(
        f'Signal received: {signal_number}; Frame: {frame}',
        source='watering_controller/controller/gracefully_stop',
        source_module='watering_controller'
    )
    logging(
        'Terminating the process',
        source='watering_controller/controller/gracefully_stop',
        source_module='watering_controller'
    )

    close_all_circuits()

    raise SystemExit(f'[{get_datetime(in_str=True)}] - [HOME APP] Gracefully stopping...')


STOP_WATERING:bool = False

SCHEDULED_PROGRAMS:list = []

# Close all circuits as sanity check
close_all_circuits()

# Register the signals to be caught
signal.signal(signal.SIGHUP, gracefully_stop)
signal.signal(signal.SIGINT, gracefully_stop)
signal.signal(signal.SIGTERM, gracefully_stop)
# signal.signal(signal.SIGQUIT, gracefully_stop)
# signal.signal(signal.SIGILL, gracefully_stop)
# signal.signal(signal.SIGTRAP, gracefully_stop)
# signal.signal(signal.SIGABRT, gracefully_stop)
# signal.signal(signal.SIGBUS, gracefully_stop)
# signal.signal(signal.SIGFPE, gracefully_stop)
# signal.signal(signal.SIGKILL, gracefully_stop)
# signal.signal(signal.SIGUSR1, gracefully_stop)
# signal.signal(signal.SIGSEGV, gracefully_stop)
# signal.signal(signal.SIGUSR2, gracefully_stop)
# signal.signal(signal.SIGPIPE, gracefully_stop)
# signal.signal(signal.SIGALRM, gracefully_stop)

# Create a daemon thread to keep the control of the scheduled programs
thread = threading.Thread(name='scheduled_programs_daemon', target=scheduled_programs_daemon)
thread.setDaemon(True)
thread.start()
