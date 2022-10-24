import asyncio
import os
import unittest
from datetime import datetime, timedelta
from typing import List

from fastiot.core.broker_connection import NatsBrokerConnection
from fastiot.core.time import get_time_now
from fastiot.db.influxdb_helper_fn import get_new_async_influx_client_from_env
from fastiot.db.mongodb_helper_fn import get_mongodb_client_from_env
from fastiot.env import env_mongodb
from fastiot.env.env import env_influxdb
from fastiot.msg import Thing
from fastiot.msg.custom_db_data_type_conversion import to_mongo_data
from fastiot.testlib import populate_test_env
from fastiot_core_services.dash.model.historic_sensor import ThingSeries, HistoricSensor
from fastiot_core_services.dash.utils import thing_series_from_mongodb_data_set, thing_series_to_mongodb_data_set


class TestThingSeries(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        populate_test_env()
        self._db_client = get_mongodb_client_from_env()
        self._database = self._db_client.get_database(env_mongodb.name)
        self._db_col = self._database.get_collection('things')
        self.influx_client = await get_new_async_influx_client_from_env()
        await asyncio.sleep(0.1)

    async def asyncTearDown(self):
        await self.influx_client.close()

    def store_test_things(self) -> List[Thing]:
        thing_list = []
        count = 0
        for i in range(4):
            for j in range(5):
                count += 1
                thing = Thing(machine="test_machine", name=f"my_sensor_{i}", measurement_id="12345",
                              value=(i + 1) * (j + 1), timestamp=datetime(year=2022, month=10, day=1, second=count))
                thing_list.append(thing)

        for thing in thing_list:
            subject_name = thing.get_subject(name=thing.name).name
            timestamp = thing.timestamp
            mongo_data = to_mongo_data(timestamp=timestamp, subject_name=subject_name, msg=thing.dict())
            self._db_col.insert_one(mongo_data)

        return thing_list

    async def test_thing_series_from_mongo_data(self):
        self._db_col.delete_many({})
        thing_list = self.store_test_things()
        result = self._db_col.find({}).sort("timestamp", 1)
        thing_series = thing_series_from_mongodb_data_set(list(result))
        self.assertListEqual(thing_list, thing_series.thing_list)

    def test_thing_series_to_mongo_data(self):
        self._db_col.delete_many({})
        thing_list = self.store_test_things()
        mongo_data_set = thing_series_to_mongodb_data_set(ThingSeries(dt_start=thing_list[0].timestamp,
                                                                      dt_end=thing_list[0].timestamp,
                                                                      thing_list=thing_list))
        self.assertTrue(len(mongo_data_set), 3 * 5)

    def test_historic_sensor(self):
        self._db_col.delete_many({})
        historic_sensor_list = []
        sensor_dict = {"sensors": [
            {"name": "my_sensor_0", "machine": "test_machine", "service": "producer"},
            {"name": "my_sensor_1", "machine": "test_machine", "service": "producer"},
            {"name": "my_sensor_2", "machine": "test_machine", "service": "producer"}
        ]}
        dt_start = datetime(year=2022, month=10, day=1, second=0)
        dt_end = datetime(year=2022, month=10, day=1, second=20)
        _ = self.store_test_things()
        for sensor in sensor_dict["sensors"]:
            historic_sensor = HistoricSensor(sensor.get("name"),
                                             sensor.get("machine"),
                                             "producer",
                                             sensor.get("service"))
            result = self._db_col.find({
                "_timestamp": {'$gte': dt_start, '$lte': dt_end},
                "name": sensor.get("name"),
                "machine": sensor.get("machine")
            })
            historic_sensor.historic_sensor_data = thing_series_from_mongodb_data_set(list(result))
            historic_sensor.historic_sensor_data.remove_until(dt_start)
            historic_sensor.historic_sensor_data.remove_from(dt_end)
            historic_sensor_list.append(historic_sensor)
        pass

    async def write_thing_to_influxdb(self):
        thing_list = []
        count = 0
        for i in range(4):
            for j in range(5):
                count += 1
                thing = Thing(machine="test_machine", name=f"my_sensor_{i}", measurement_id="12345",
                              value=(i + 1) * (j + 1), timestamp=get_time_now() + timedelta(seconds=count))
                thing_list.append(thing)

        for thing in thing_list:
            data = [{"measurement": str(thing.name),
                     "tags": {"machine": str(thing.machine),
                              "unit": str(thing.unit)},
                     "fields": {"value": thing.value},
                     "time": thing.timestamp
                     }]
            await self.influx_client.write_api().write(bucket=env_influxdb.bucket, org=env_influxdb.organisation,
                                                       record=data, precision='ms')


    async def test_influxdb_query(self):
        await self.write_thing_to_influxdb()
        dt_start = get_time_now() - timedelta(seconds=10)
        dt_end = get_time_now() - timedelta(seconds=50)


if __name__ == '__main__':
    unittest.main()
