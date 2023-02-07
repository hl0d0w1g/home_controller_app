'''
Utils
'''

import json
import os
import itertools
from schema import Schema, And, Use # pylint: disable=import-error

from home_controller.config import WATERING_N_CIRCUITS, WATERING_N_PROGRAMS
from home_controller.utils import (
    logging, check_object_schema, read_env_varaible,
    SPANISH_WEEKDAYS_SHORT, HOUR_RE_PATTERN
)


# Watering configuration json file schema
WATERING_CONFIG_SCHEMA = Schema({
    And(Use(str), lambda n: 1 <= int(n) <= WATERING_N_PROGRAMS): {
        'selected': Use(bool),
        'circuits': {
            And(Use(str), lambda n: 1 <= int(n) <= WATERING_N_CIRCUITS): {
                'activated': Use(bool),
                'time': Use(int),
            }
        },
        'days': {
            And(Use(str), lambda n: n in SPANISH_WEEKDAYS_SHORT): Use(bool)
        },
        'starts': {
            And(Use(str), lambda n: 1 <= int(n) <= 3): {
                'activated': Use(bool),
                'hour': And(
                    Use(str),
                    lambda n: len(n) == 5 and HOUR_RE_PATTERN.match(n) is not None
                ),
            }
        }
    }
})


def weekday_time_combinations(days:list, times:list) -> list:
    '''
    Returns a list with the hour and day of the week for each combination of days and times

    Args:
    - days (list): List of days of the week
    - times (list): List of times of the day

    Return:
    - combinations (list): List with the hour and day of the week
                            for each combination of days and times
    '''
    assert isinstance(days, list)
    assert isinstance(times, list)
    return list(itertools.product(days, times))

def read_watering_config() -> dict:
    '''
    Read watering configuration from disk

    Args:
    - None

    Return:
    - config (dict): Watering configuration readed from disk
    '''
    logging(
        'Reading watering configuration from disk',
        source='watering_controller/utils/read_watering_config',
        source_module='watering_controller'
    )

    with open(
            WATERING_CONFIG_FILE,
            encoding='utf-8'
        ) as file:
        config = json.load(file)

    if check_object_schema(WATERING_CONFIG_SCHEMA, config):
        return config

    return {}

def save_watering_config(config:dict) -> bool:
    '''
    Save watering configuration to disk

    Args:
    - config (dict): Watering configuration dictionary

    Return:
    - Save opetation status. True if successful, False otherwise.
    '''
    assert isinstance(config, dict)
    assert check_object_schema(WATERING_CONFIG_SCHEMA, config)
    logging(
        'Saving watering configuration to disk',
        source='watering_controller/utils/save_watering_config',
        source_module='watering_controller'
    )

    try:
        with open(
                WATERING_CONFIG_FILE,
                'w',
                encoding='utf-8'
            ) as file:
            json.dump(config, file)

        return True

    except FileNotFoundError:
        return False


WATERING_CONFIG_FILE:str = read_env_varaible('CONFIG_DIR', './config') + '/watering_config.json'
