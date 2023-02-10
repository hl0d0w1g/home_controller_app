"""
Useful functions for the whole app
"""

import os
import time
import re
import datetime
from typing import Union
# import logging
from schema import Schema, SchemaError # pylint: disable=import-error

from home_controller import socketio

# Abbreviations for the days of the week in Spanish
SPANISH_WEEKDAYS_SHORT:set = set({'L', 'M', 'X', 'J', 'V', 'S', 'D'})
# Regex pattern for the time string
TIME_RE_PATTERN = re.compile("^([01]?[0-9]|2[0-3]):[0-5][0-9]")
# Datetime string format
DATETIME_FMT:str = '%Y-%m-%d %H:%M:%S'

# logging.basicConfig(filename=os.path.join(
#                                 os.path.dirname(os.path.abspath(__file__)), LOG_FILE_PATH
#                             ),
#                     format='%(asctime)s - - %(levelname)s:%(message)s',
#                     datefmt='%Y-%m-%d %H:%M:%S',
#                     level=logging.WARNING)


def pause(secs:Union[int, float]) -> None:
    '''
    Delay execution for a given number of seconds. The argument may be a
    floating point number for sub second precision.

    Args:
    - secs (int, float): Number of seconds to pause

    Return:
    - None
    '''
    assert isinstance(secs, (int, float)), 'You should provide int or float instead'
    time.sleep(secs)

def get_datetime(timedelta:Union[dict, None]=None, in_str:bool=False) -> Union[datetime.datetime, str]:
    '''
    Returns the current datetime plus the specified time delta

    Args:
    - timedelta (dict): Timedelta to add in dict format {"days": d, "seconds": s, ...}
    - in_str (bool): If the datetime should be returned in string or datetime type

    Return:
    - datetime (datetime.datetime, str): Current datetime plus provided timedelta
    '''
    assert isinstance(timedelta, (dict, type(None))), \
        '''You should provide a time delta in format: {"days": d, "seconds": s, ...}. 
        More info: https://docs.python.org/es/3/library/datetime.html#timedelta-objects'''
    assert isinstance(in_str, bool), 'You should provide a boolean'

    now = datetime.datetime.now()

    if timedelta:
        now += datetime.timedelta(**timedelta)

    if in_str:
        return now.strftime(DATETIME_FMT)

    return now

def read_env_variable(name:str, default:str) -> str:
    '''
    Read an environment variable

    Args:
    - name (str): Name of the environment variable
    - default (str): Default value to return if the environment variable is not set

    Return:
    - value (str): Value of the environment variable if it is set, default otherwise
    '''
    assert isinstance(name, str), 'You should provide a string'
    assert isinstance(default, str), 'You should provide a string'

    env_var = os.getenv(name, default=default)

    return env_var

def logging(message:str, source_module:str, source_function:str, level:str='INFO') -> None:
    '''
    Prints log and add it into the log file

    Args:
    - message (str): Message to be saved into log file
    - source_module (str): Source module of the log
    - source_function (str): Source function of the log
    - level (str): Importance level of the log. Default: INFO

    Return:
    - None
    '''
    # if level == 'INFO':
    #     logging.info(f'({source}) {message}')
    # elif level == 'WARNING':
    #     logging.warning(f'({source}) {message}')
    assert isinstance(message, str), 'You should provide a string'
    assert isinstance(source_module, str), 'You should provide a string'
    assert isinstance(source_function, str), 'You should provide a string'
    assert isinstance(level, str), 'You should provide a string'

    log_msg = f'[{get_datetime(in_str=True)}] - [{level}] ({source_module}/{source_function}) {message}'

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
    - namespace (str): Namespace through which the message is emitted

    Return:
    - None
    '''
    assert isinstance(route, str), 'You should provide a string'
    assert isinstance(message, str), 'You should provide a string'
    assert isinstance(namespace, str), 'You should provide a string'
    socketio.emit(route, message, namespace=namespace)

def time_str_to_time(time_str:str) -> datetime.time:
    '''
    Returns a datetime.time object from a string with the time in format HH:MM

    Args:
    - time (str): String time to be converted into datetime type

    Return:
    - time (datetime.time)
    '''
    assert(isinstance(time_str, str) and len(time_str) == 5 and TIME_RE_PATTERN.match(time_str) is not None), \
        'Time should be provided as string in format HH:MM'

    return datetime.time.fromisoformat(time_str)

def check_object_schema(obj_schema:Schema, obj:dict) -> bool:
    '''
    Check if an object is valid according to a schema

    Args:
    - obj_schema (Schema): Schema that the object must fit
    - obj (dict): Object to check

    Return:
    - Check result (bool)
    '''
    assert isinstance(obj_schema, Schema)
    assert isinstance(obj, dict)

    try:
        obj_schema.validate(obj)
        return True
    except SchemaError as error:
        logging(
            error,
            source_module='home_controller',
            source_function='utils/check_object_schema'
        )
        return False


# Directory where all the logs will be saved
LOG_FILEs_DIR:str = read_env_variable('LOGS_DIR', 'logs')
