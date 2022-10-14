from datetime import datetime
from typing import Optional, List
from calendar import timegm

# import numpy as np
# import pandas as pd

# from sam.msg import TimeSeriesData
import pytz
from pydantic import BaseModel, validator

from fastiot.msg import Thing


class HistoricSensor:
    def __init__(self, name, machine, customer, module):
        self.historic_sensor_data: Optional[Thing] = None
        self.name = name
        self.machine = machine
        self.customer = customer
        self.module = module

    """def get_min(self, historic_sensors_list, dashboard):
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

        return timegm(result.utctimetuple())"""

    """def get_max(self, historic_sensors_list, dashboard):
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
        return timegm(result.utctimetuple())"""

    """@staticmethod
    def to_df(historic_sensor_list: List['HistoricSensor']):
        historic_sensor_df_list = [
            pd.DataFrame(historic_sensor.historic_sensor_data.values, columns=['datetime', historic_sensor.name])
            for counter, historic_sensor in enumerate(historic_sensor_list)]

        historic_sensors_df = pd.concat(historic_sensor_df_list, axis=1)
        _, i = np.unique(historic_sensors_df.columns, return_index=True)
        historic_sensors_df = historic_sensors_df.iloc[:, i]

        historic_sensors_df = historic_sensors_df.set_index('datetime')
        return historic_sensors_df"""


class ThingSeries(BaseModel):
    """
    This class is used to store a list of Things with the same machine and name
    """
    dt_start: Optional[datetime]
    dt_end: Optional[datetime]
    machine: Optional[str]
    name: Optional[str]
    thing_list: List[Thing]

    def __init__(self, **vars):
        vars["machine"] = thing_list[0].machine
        vars["name"] = thing_list[0].name
        vars["dt_start"] = thing_list[0].timestamp
        vars["dt_end"] = thing_list[-1].timestamp
        super().__init__(**vars)

    def remove_until(self, timestamp: datetime):
        """
        Removes all data until timestamp. It is guaranteed that if this operation finishes successfully, the values
        starting from 2nd until the end of the time series will be greater then timestamp. If the time series includes
        timestamp when the function is called, it still will after it finishes.

        The dt_start attribute will be adjusted accordingly. No timestamps of values will be changed.

        :param timestamp: Timestamp used for removal.
        """
        while len(self.thing_list) > 1:
            if self.thing_list[0].timestamp <= timestamp:
                self.thing_list.pop(0)
            else:
                break
        self.dt_start = self.thing_list[0].timestamp

    def remove_from(self, timestamp: datetime):
        while len(self.thing_list) > 1:
            if self.thing_list[-1].timestamp >= timestamp:
                self.thing_list.pop()
            else:
                break
        self.dt_end = self.thing_list[-1].timestamp


if __name__ == '__main__':
    thing_list = [Thing(machine='machine', name=f'sensor_0', measurement_id=f'123_{i}', value=i * 2,
                        timestamp=datetime(year=2022, month=10, day=1, second=i)) for i in range(10)]
    thing_series = ThingSeries(thing_list=thing_list)
    dt_start = datetime(year=2022, month=10, day=1, second=3)
    thing_series.remove_until(dt_start)
    dt_end = datetime(year=2022, month=10, day=1, second=7)
    thing_series.remove_from(dt_end)
