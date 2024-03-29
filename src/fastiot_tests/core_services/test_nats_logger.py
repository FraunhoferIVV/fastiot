import asyncio
import os
import unittest
from datetime import datetime

from fastiot.core.broker_connection import NatsBrokerConnection
from fastiot.core.time import get_time_now
from fastiot.msg.thing import Thing
from fastiot.testlib import populate_test_env
from fastiot_core_services.nats_logger.env import FASTIOT_NATS_LOGGER_FILTER_FIELD, FASTIOT_NATS_LOGGER_FILTER_VALUE
from fastiot_core_services.nats_logger.nats_logger_module import NatsLoggerService

MESSAGE = Thing(machine='SomeMachine', name="LoggedSensor", value=24, timestamp=get_time_now(), measurement_id="1")


class TestNatsLogger(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        populate_test_env()
        self.broker_connection = await NatsBrokerConnection.connect()

    async def test_unfiltered(self):
        async with NatsLoggerService() as _:
            with self.assertLogs(level="INFO") as capture:
                try:
                    await self.broker_connection.publish(Thing.get_subject(name='unfiltered'), MESSAGE)
                    await asyncio.sleep(0.01)
                finally:
                    self.assertTrue(MESSAGE.name in capture.output[0])

    async def test_filtered(self):
        os.environ[FASTIOT_NATS_LOGGER_FILTER_FIELD] = 'value'
        os.environ[FASTIOT_NATS_LOGGER_FILTER_VALUE] = '25'
        async with NatsLoggerService() as _:
            with self.assertLogs(level="INFO") as capture:
                try:
                    await self.broker_connection.publish(Thing.get_subject(name='filtered'), MESSAGE)
                    new_msg = MESSAGE
                    new_msg.value = 25
                    await self.broker_connection.publish(Thing.get_subject(name='filtered'), MESSAGE)
                    await asyncio.sleep(0.02)

                finally:
                    self.assertEqual(1, len(capture.output))
                    self.assertTrue(str(new_msg.value) in capture.output[0])

                    os.environ.pop(FASTIOT_NATS_LOGGER_FILTER_FIELD)
                    os.environ.pop(FASTIOT_NATS_LOGGER_FILTER_VALUE)


if __name__ == '__main__':
    unittest.main()
