"""
Controller functions of the watering module
"""

import threading
import signal

from home_controller.config import WATERING_N_CIRCUITS, WATERING_N_PROGRAMS, WATERING_NAMESPACE
from home_controller.io import WATERING_0, WATERING_1, WATERING_2, WATERING_3, WATERING_ANY
from home_controller.utils import logging, socket_emit, get_datetime, pause

from .program import Program, ScheduledProgram
from .utils import save_watering_config, read_watering_config, weekday_time_combinations


def init_program(idx: int) -> None:
    '''
    Init program by id

    Args
    - idx (int): Identifier of the program to initiate

    Return
    - None
    '''
    assert (
        isinstance(idx, int) and 1 <= idx <= WATERING_N_PROGRAMS
    ), 'Provide an integer program id between 1 and ' + str(WATERING_N_PROGRAMS)

    # Deactivate STOP_WATERING flag
    resume_watering()

    # Create the program and execute it within a thread
    program = ScheduledProgram(idx, 'L', '00:00')
    threading.Thread(target=program.execute, args=(is_watering_stopped,)).start()


def init_circuit(idx: int, mins: int) -> None:
    '''
    Execute circuit by id during the indicated mins

    Args:
    - idx (int): Identifier of the program to initiate
    - mins (int): Minutes during which the circuit is active

    Return:
    - None
    '''
    assert (
        isinstance(idx, int) and 1 <= idx <= WATERING_N_CIRCUITS
    ), 'Provide an integer circuit id between 1 and ' + str(WATERING_N_CIRCUITS)
    assert isinstance(mins, int) and mins >= 0, 'Provide a valid integer of minutes'

    # Deactivate STOP_WATERING flag
    resume_watering()

    # Create a program of only one circuit and execute it within a thread
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
        source_module='watering_controller',
        source_function='controller/close_all_circuits',
    )

    watering_pins = [WATERING_3, WATERING_2, WATERING_1, WATERING_0, WATERING_ANY]

    for pin in watering_pins:
        logging(
            f'Pin {pin.pin} deactivated',
            source_module='watering_controller',
            source_function='controller/close_all_circuits',
        )
        pin.deactivate()


def new_scheduled_programs_config(config: dict) -> None:
    '''
    Update the list of scheduled programs

    Args:
    - config (dict): Watering configuration dictionary

    Return:
    - None
    '''
    assert isinstance(config, dict), 'You should provide a dictionary'

    scheduled_programs = create_scheduled_programs(config)
    update_scheduled_programs(scheduled_programs)
    save_watering_config(config)


def create_scheduled_programs(config: dict) -> list:
    '''
    Create a the list of scheduled_programs

    Args:
    - config (dict): Watering configuration dictionary

    Return:
    - scheduled_programs (list(ScheduledProgram)): List of ScheduledProgram objects
    '''
    assert isinstance(config, dict), 'You should provide a dictionary'

    scheduled_programs_ls = []
    for program_id, program_info in config.items():
        if program_info['selected']:
            program_days = [day for day, activated in program_info['days'].items() if activated]
            program_starts = [
                start_info['hour']
                for start_id, start_info in program_info['starts'].items()
                if start_info['activated']
            ]
            scheduled_programs = weekday_time_combinations(program_days, program_starts)
            scheduled_programs = [
                ScheduledProgram(int(program_id), day, hour)
                for (day, hour) in scheduled_programs
                if day and hour
            ]
            scheduled_programs_ls += scheduled_programs

    logging(
        f'Creating scheduled_programs: {scheduled_programs_ls}',
        source_module='watering_controller',
        source_function='controller/create_scheduled_programs',
    )

    return scheduled_programs_ls


def update_scheduled_programs(new_scheduled_programs: list) -> None:
    '''
    Update the list of scheduled_programs

    Args:
    - new_scheduled_programs (list): List of tuples with the new scheduled_programs

    Return:
    - None
    '''
    assert isinstance(new_scheduled_programs, list), 'You should provide a list'

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
    global SCHEDULED_PROGRAMS  # , STOP_WATERING
    config = read_watering_config()
    SCHEDULED_PROGRAMS = create_scheduled_programs(config)

    while True:
        program_to_execute = next((p for p in SCHEDULED_PROGRAMS if p.check_schedule()), None)
        if program_to_execute is not None:
            logging(
                f'Executing Program: {program_to_execute}',
                source_module='watering_controller',
                source_function='controller/scheduled_programs_daemon',
            )
            threading.Thread(target=program_to_execute.execute, args=(is_watering_stopped,)).start()
            pause(60)
        else:
            pause(15)


def is_watering_stopped() -> bool:
    '''
    Return True if the watering should be stopped, False otherwise

    Args:
    - None

    Return:
    - None
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

    socket_emit('stop-watering', {}, WATERING_NAMESPACE)


def resume_watering() -> None:
    '''
    Set to false the STOP_WATERING flag

    Args:
    - None:

    Return:
    - None
    '''
    global STOP_WATERING
    STOP_WATERING = False


def gracefully_stop(signal_number: int, frame) -> None:
    '''
    Managing signals to close all circuits before continue

    Args:
    - signal_number (int): Signal id which is been captured
    - frame (None, Frame): The current stack frame

    Return:
    - None
    '''
    logging(
        f'Signal received: {signal_number}; Frame: {frame}',
        source_module='watering_controller',
        source_function='controller/gracefully_stop',
    )
    logging(
        'Terminating the process',
        source_module='watering_controller',
        source_function='controller/gracefully_stop',
    )

    close_all_circuits()

    raise SystemExit(f'[{get_datetime(in_str=True)}] - [HOME APP] Gracefully stopping...')


# Flag to stop watering if is requested by the user
STOP_WATERING: bool = False
# List for the programmed scheduled programs by the user
SCHEDULED_PROGRAMS: list = []

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
thread.daemon = True
thread.start()
