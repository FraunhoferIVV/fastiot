from datetime import datetime
from typing import Optional, List
from calendar import timegm

# import numpy as np
# import pandas as pd

# from sam.msg import TimeSeriesData
import numpy as np
import pandas as pd
import pytz
from pydantic import BaseModel, validator

from fastiot.msg import Thing


class ThingSeries(BaseModel):
    """
    This class is used to store a list of Things with the same machine and name
    """
    dt_start: Optional[datetime]
    dt_end: Optional[datetime]
    thing_list: List[Thing] = []

    def __init__(self, **vars):
        super().__init__(**vars)
        if self.thing_list:
            vars["dt_start"] = vars["thing_list"][0].timestamp
            vars["dt_end"] = vars["thing_list"][-1].timestamp
            super().__init__(**vars)

    def remove_until(self, timestamp: datetime):
        """
        Removes all data until timestamp. It is guaranteed that if this operation finishes successfully, the values
        starting from 2nd until the end of the time series will be greater then timestamp. If the time series includes
        timestamp when the function is called, it still will after it finishes.

        The dt_start attribute will be adjusted accordingly. No timestamps of values will be changed.

        :param timestamp: Timestamp used for removal.
        """
        if self.thing_list:
            while len(self.thing_list) > 1:
                if self.thing_list[0].timestamp <= timestamp:
                    self.thing_list.pop(0)
                else:
                    break
            self.dt_start = self.thing_list[0].timestamp

    def remove_from(self, timestamp: datetime):
        if self.thing_list:
            while len(self.thing_list) > 1:
                if self.thing_list[-1].timestamp >= timestamp:
                    self.thing_list.pop()
                else:
                    break
            self.dt_end = self.thing_list[-1].timestamp


class HistoricSensor:
    def __init__(self, name, machine, customer, service):
        self.historic_sensor_data: Optional[ThingSeries] = None
        self.name = name
        self.machine = machine
        self.customer = customer
        self.service = service

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

    @staticmethod
    def to_df(historic_sensor_list: List['HistoricSensor']):
        historic_sensor_df_list = [
            pd.DataFrame(
                [(thing.timestamp, thing.value) for thing in historic_sensor.historic_sensor_data.thing_list],
                columns=['datetime', historic_sensor.name])
            for counter, historic_sensor in enumerate(historic_sensor_list)]

        historic_sensors_df = pd.concat(historic_sensor_df_list, axis=0)
        _, i = np.unique(historic_sensors_df.columns, return_index=True)
        historic_sensors_df = historic_sensors_df.iloc[:, i]
        historic_sensors_df['datetime'] = historic_sensors_df['datetime'].dt.tz_localize(None)

        historic_sensors_df = historic_sensors_df.set_index('datetime')
        return historic_sensors_df
