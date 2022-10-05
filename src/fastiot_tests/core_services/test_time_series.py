import asyncio
import unittest
from datetime import datetime, timedelta


from fastiot.core.broker_connection import NatsBrokerConnection

from fastiot.db.influxdb_helper_fn import get_influxdb_client_from_env
from fastiot.env.env import env_influxdb

from fastiot.msg.hist import HistObjectReq, HistObjectResp
from fastiot.msg.thing import Thing
from fastiot_core_services.time_series.time_series_service import TimeSeriesService
from fastiot_tests.generated import set_test_environment

THING = Thing(machine='SomeMachine', name="RequestSensor", value=42, timestamp=datetime.now(), measurement_id="1")


class TestTimeSeries(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        set_test_environment()
        self.client = get_influxdb_client_from_env()
        self.broker_connection = await NatsBrokerConnection.connect()

    async def _start_service(self):
        service = TimeSeriesService(broker_connection=self.broker_connection)
        self.service_task = asyncio.create_task(service.run())
        await self.delete_data()
        await asyncio.sleep(0.005)

    async def insert_data(self):
        for i in range(5):
            thing_msg = Thing(machine='test_machine', name=f'sensor_{i}',
                              value=1, timestamp=f"2019-07-25T21:48:0{i}Z")

            await self.broker_connection.publish(Thing.get_subject(thing_msg.name), thing_msg)
            await asyncio.sleep(0.05)

    async def delete_data(self):
        self.client.delete_api().delete(stop="2024-01-01T00:00:00Z", start="1970-01-01T00:00:00Z",
                                        bucket=env_influxdb.bucket, predicate='machine="test_machine"',
                                        org=env_influxdb.organisation)

    async def asyncTearDown(self):
        self.service_task.cancel()

    async def test_storage(self):
        await self._start_service()
        await self.insert_data()
        query = \
            f'from(bucket: "{env_influxdb.bucket}") ' \
            '|> range(start: 2019-07-25T21:47:00Z)' \
            '|> group(columns: ["time"])' \
            '|> sort(columns: ["time"])' \
            '|> filter(fn: (r) => r["machine"] == "test_machine")'
        tables = self.client.query_api().query(query, org=env_influxdb.organisation)
        i = 0
        for table in tables:
            for row in table:
                self.assertEqual(f'sensor_{i}', row.get_measurement())
                i = i + 1
        await self.delete_data()

    async def test_reply_standart(self):
        await self._start_service()
        for i in range(5):
            thing_msg = Thing(machine='test_machine', name=f'sensor_{i}',
                              value=1, timestamp=datetime.utcnow())
            await self.broker_connection.publish(Thing.get_subject(thing_msg.name), thing_msg)
            await asyncio.sleep(0.05)

        subject = HistObjectReq.get_reply_subject(name="things")
        reply: HistObjectResp = await self.broker_connection.request(subject=subject,
                                                                     msg=HistObjectReq(machine="test_machine",
                                                                                       timeout=10))
        for i in range(5):
            self.assertEqual(f'sensor_{i}'
                             , reply.values[i].get("sensor"))
        await self.delete_data()

    async def test_reply_start_end(self):
        await self._start_service()
        await self.insert_data()
        subject = HistObjectReq.get_reply_subject(name="things")
        reply: HistObjectResp = await self.broker_connection.request(subject=subject,
                                                                     msg=HistObjectReq(machine="test_machine",
                                                                                       dt_start='2019-07-25T21:47:00Z',
                                                                                       dt_end='2019-07-25T21:48:04Z',
                                                                                       timeout=10))
        for i in range(4):
            self.assertEqual({"machine": 'test_machine',
                              "sensor": f'sensor_{i}',
                              "value": "1 ",
                              "timestamp": f"2019-07-25T21:48:0{i}+00:00",
                              }, reply.values[i])
        with self.assertRaises(IndexError):
            reply.values[4]

        await self.delete_data()


if __name__ == '__main__':
    unittest.main()
