import datetime
from typing import Optional, List
from calendar import timegm

import numpy as np
import pandas as pd

from sam.msg import TimeSeriesData
import pytz


class HistoricSensor:
    def __init__(self, name, machine, customer, module):
        self.historic_sensor_data: Optional[TimeSeriesData] = None
        self.name = name
        self.machine = machine
        self.customer = customer
        self.module = module

    def get_min(self, historic_sensors_list, dashboard):
        result = pytz.UTC.localize(datetime.datetime.max)
        for sensor in dashboard.get("sensors"):
            for historic_sensor in historic_sensors_list:
                if historic_sensor.name == sensor.get("name") and historic_sensor.machine == sensor.get("machine"):
                    try:
                        if result > historic_sensor.historic_sensor_data.dt_start:
                            result = historic_sensor.historic_sensor_data.dt_start
                    except AttributeError:
                        print(
                            "Sensor " + sensor.get("name") + " of machine" + sensor.get("machine") + " failed to load")
                        return 0

        return timegm(result.utctimetuple())

    def get_max(self, historic_sensors_list, dashboard):
        result = pytz.UTC.localize(datetime.datetime.min)
        for sensor in dashboard.get("sensors"):
            for historic_sensor in historic_sensors_list:
                if historic_sensor.name == sensor.get("name") and historic_sensor.machine == sensor.get("machine"):
                    try:
                        if result < historic_sensor.historic_sensor_data.dt_end:
                            result = historic_sensor.historic_sensor_data.dt_end
                    except AttributeError:
                        print(
                            "Sensor " + sensor.get("name") + " of machine" + sensor.get("machine") + " failed to load")
                        return 0
        return timegm(result.utctimetuple())

    @staticmethod
    def to_df(historic_sensor_list: List['HistoricSensor']):
        historic_sensor_df_list = [
            pd.DataFrame(historic_sensor.historic_sensor_data.values, columns=['datetime', historic_sensor.name])
            for counter, historic_sensor in enumerate(historic_sensor_list)]

        historic_sensors_df = pd.concat(historic_sensor_df_list, axis=1)
        _, i = np.unique(historic_sensors_df.columns, return_index=True)
        historic_sensors_df = historic_sensors_df.iloc[:, i]

        historic_sensors_df = historic_sensors_df.set_index('datetime')
        return historic_sensors_df
