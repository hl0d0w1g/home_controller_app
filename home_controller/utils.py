'''
Utils
'''

import os
import time
import re
import datetime
from typing import Union
# import logging
from schema import SchemaError # pylint: disable=import-error

from home_controller import socketio

# Abreviations for the days of the week in spanish
SPANISH_WEEKDAYS_SHORT:set = set({'L', 'M', 'X', 'J', 'V', 'S', 'D'})
# Regex pattern for the hour string
HOUR_RE_PATTERN = re.compile("^([01]?[0-9]|2[0-3]):[0-5][0-9]")
# Datetime string format
DATETIME_FMT:str = '%Y-%m-%d %H:%M:%S'

# logging.basicConfig(filename=os.path.join(
#                                 os.path.dirname(os.path.abspath(__file__)), LOG_FILE_PATH
#                             ),
#                     format='%(asctime)s - - %(levelname)s:%(message)s',
#                     datefmt='%Y-%m-%d %H:%M:%S',
#                     level=logging.WARNING)


def pause(secs:float) -> None:
    '''
    Delay execution for a given number of seconds. The argument may be a
    floating point number for subsecond precision.
    '''
    time.sleep(secs)

def get_datetime(timedelta:dict=None, in_str:bool=False) -> Union[datetime.datetime, str]:
    '''
    Returns the specefied datetime
    '''
    now = datetime.datetime.now()

    if timedelta:
        now += datetime.timedelta(**timedelta)

    if in_str:
        return now.strftime(DATETIME_FMT)
        
    return now

def read_env_varaible(name:str, default:str) -> str:
    '''
    Read an environment variable

    Args:
    - name (str): Name of the environment variable
    - default (str): Default value to return if the environment variable is not set

    Return:
    - value (str): Value of the environment variable if it is set, default otherwise
    '''
    assert isinstance(name, str)
    assert isinstance(default, str)

    env_var = os.getenv(name, default=default)

    return env_var

def logging(message:str, level:str='INFO', source:str='', source_module:str='logs') -> None:
    '''
    Adds a new log into the log file

    Args:
    - message (str): Message to be saved into log file
    - level (str): Importance level of the log
    - source (str): Source file of the log

    Return:
    - None
    '''
    # if level == 'INFO':
    #     logging.info(f'({source}) {message}')
    # elif level == 'WARNING':
    #     logging.warning(f'({source}) {message}')

    log_msg = f'[{get_datetime(in_str=True)}] - [{level}] ({source}) {message}'

    print(log_msg)

    log_file = LOG_FILEs_DIR + f'/{source_module}.log'
    mode = 'a' if os.path.exists(log_file) else 'w'
    with open(log_file, mode, encoding='utf-8') as logsf:
        logsf.write(f'{log_msg}\n')

def socket_emit(route:str, message:dict, namespace:str='/') -> None:
    '''
    Emit messages through the socket

    Args:
    - route (str): Route where send the message
    - message (dict): Dictionary with params to be sent

    Return:
    - None
    '''
    socketio.emit(route, message, namespace=namespace)

def hour_str_to_time(hour:str) -> datetime.time:
    '''
    Returns a datetime.time object from a string with the hour with format HH:MM
    '''
    assert(isinstance(hour, str) and len(hour) == 5 and HOUR_RE_PATTERN.match(hour) is not None)

    return datetime.time.fromisoformat(hour)

def check_object_schema(obj_schema, obj) -> bool:
    '''
    Check if an object is valid according to a schema
    '''
    try:
        obj_schema.validate(obj)
        return True
    except SchemaError as error:
        logging(
            error,
            source='home_controller/utils/check_object_schema',
            source_module='home_controller'
        )
        return False


LOG_FILEs_DIR:str = read_env_varaible('LOGS_DIR', 'logs')
