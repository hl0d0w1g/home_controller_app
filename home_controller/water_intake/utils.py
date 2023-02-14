"""
Useful functions for the water intake module
"""

import os

# import pandas as pd

from home_controller.config import WATER_FLOW_SENSOR_MEASUREMENT_FREQUENCY
from home_controller.utils import logging, read_env_variable, get_datetime, DATETIME_FMT


def save_flow_measurement(datetime: str, flow: float) -> None:
    '''
    Save the last flow measurement record

    Args:
    - datetime (str): Datetime of the flow measure
    - flow (float): Water flow measure

    Return:
    - None
    '''
    assert isinstance(datetime, str), 'You should provide a string datetime'
    assert isinstance(flow, float), 'You should provide a float'

    with open(FLOW_24H_FILE, 'a+', encoding='utf-8') as flowf:
        data = flowf.readlines()

        data.append(f'{datetime},{flow}\n')

        # The file only stores the last 24 hours of flow data
        # 86400 = seconds per day (60*60*24)
        # 100 = margin to avoid lose of data due to rounding errors
        if len(data) > ((WATER_FLOW_SENSOR_MEASUREMENT_FREQUENCY * 86400) + 100):
            data = data[1:]

        flowf.seek(0)
        flowf.writelines(data)
        flowf.truncate()


def read_flow_measurement(requested_data_points: int) -> dict:
    '''
    Get N last flow measurements from the file stores on disk

    Args:
    - requested_data_points (int): Number of flow measurements to return

    Return:
    - Requested flow measurements data points as dict {'datetime': [], 'flow': []}
    '''
    assert (
        isinstance(requested_data_points, int) and requested_data_points > 0
    ), 'You should provide a positive integer > 0'

    last_flow_sensor_data = {'datetime': [], 'flow': []}
    if os.path.exists(FLOW_24H_FILE):
        with open(FLOW_24H_FILE, 'r', encoding='utf-8') as flowf:
            data = flowf.readlines()[-requested_data_points:]
            data = [d.split(',') for d in data]
            last_flow_sensor_data['datetime'] = [d[0].split(' ')[1] for d in data]
            last_flow_sensor_data['flow'] = [d[1].replace('\n', '') for d in data]

    return last_flow_sensor_data


# def aggregates_flow_data(flow_data:list) -> int:
#     '''
#     Sum all the flow data to compute the final consumption
#     '''
#     assert isinstance(flow_data, list)

#     flow_data = [int(dp) * WATER_FLOW_SENSOR_MEASUREMENT_FREQUENCY for dp in flow_data]
#     return sum(flow_data)

# def save_historical_consumption() -> None:
#     '''
#     Aggregates and save to a file the flow measurements of last day
#     '''
#     date = get_datetime(timedelta={'days': -1}).strftime('%Y-%m-%d')
#     consumption = 0

#     logging(
#             f'Saving consumption of {date}',
#             source='home_controller/water_flow_sensor/utils/save_historical_consumption',
#             source_module='water_flow_sensor'
#         )

#     if os.path.exists(FLOW_24H_FILE):
#         flow_df = pd.read_csv(FLOW_24H_FILE, header=0)
#         flow_df.columns = ['datetime', 'flow']
#         flow_df['datetime'] = flow_df['datetime'].apply(lambda d: d.split(' ')[0])
#         consumption = aggregates_flow_data(flow_df.loc[flow_df['datetime'] == date]['flow'].to_list())

#     with open(CONSUMPTION_FILE, 'a+', encoding='utf-8') as consumptionf:
#         data = consumptionf.readlines()

#         data.append(f'{date},{consumption}\n')

#         # The file only stores the last 2 years of consumption data
#         # 731 = 365 + 366 (2 years including leap-year)
#         if len(data) > 731:
#             data = data[1:]

#         consumptionf.seek(0)
#         consumptionf.writelines(data)
#         consumptionf.truncate()

# def read_historical_consumption(period:str) -> dict:
#     '''
#     Read from file the flow measurements
#     '''
#     assert isinstance(period, str)
#     assert (period in ['week', 'month', 'year'])

#     date = get_datetime()

#     historical_consumption_data = {'current_period': [], 'last_period': [], 'labels': []}

#     if os.path.exists(CONSUMPTION_FILE):
#         # TO-DO: Complete data reading
#         # consumption_df = pd.read_csv(CONSUMPTION_FILE, header=0)
#         # consumption_df.columns = ['date', 'consumption']
#         # consumption_df['date'] = pd.to_datetime(consumption_df['date'], format='%Y-%m-%d').dt.date

#         if period == 'week':
#             historical_consumption_data['labels'] = ['L', 'M', 'X', 'J', 'V', 'S', 'D']

#             historical_consumption_data['current_period'] = [12, 19, 3, 5, 2, 3, 10]
#             historical_consumption_data['last_period'] = [14, 13, 6, 7, 4, 7, 11]

#         elif period == 'month':
#             historical_consumption_data['labels'] = ['S1', 'S2', 'S3', 'S4']

#             historical_consumption_data['current_period'] = [4, 9, 13, 5]
#             historical_consumption_data['last_period'] = [1, 3, 16, 7]

#         elif period == 'year':
#             historical_consumption_data['labels'] = [
#                 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
#                 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
#             ]

#             historical_consumption_data['current_period'] = [12, 19, 3, 4, 9, 13, 5, 5, 2, 3, 10, 2]
#             historical_consumption_data['last_period'] = [14, 13, 6, 7, 1, 3, 16, 7, 4, 7, 11, 9]

#         else:
#             raise ValueError('Incorrect period for historical consumption')

#     return historical_consumption_data


# File where the flow measurements of the last 24h are stored in disk
FLOW_24H_FILE: str = read_env_variable('DATA_DIR', './data') + '/flow_24h.csv'
# File where the aggregated flow data (consumption) is stored in disk
CONSUMPTION_FILE: str = read_env_variable('DATA_DIR', './data') + '/consumption.csv'
