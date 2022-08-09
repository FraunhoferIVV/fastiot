import asyncio
import os
import unittest
from datetime import datetime

from fastiot.core.broker_connection import NatsBrokerConnectionImpl
from fastiot.msg.thing import Thing
from fastiot_core_services.nats_logger.env import FASTIOT_NATS_LOGGER_FILTER_FIELD, FASTIOT_NATS_LOGGER_FILTER_VALUE
from fastiot_core_services.nats_logger.nats_logger_module import NatsLoggerService
from generated import set_test_environment

MESSAGE = Thing(machine='SomeMachine', name="LoggedSensor", value=24, timestamp=datetime.now())


class TestNatsLogger(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        set_test_environment()
        self.broker_connection = await NatsBrokerConnectionImpl.connect()

    async def _start_service(self):
        service = NatsLoggerService(broker_connection=self.broker_connection)
        self.service_task = asyncio.create_task(service.run())
        await asyncio.sleep(0.005)

    async def asyncTearDown(self):
        self.service_task.cancel()

    async def test_unfiltered(self):
        with self.assertLogs(level="INFO") as capture:
            try:
                await self._start_service()
                await self.broker_connection.publish(Thing.get_subject(name='unfiltered'), MESSAGE)
                await asyncio.sleep(0.01)
            finally:
                self.assertTrue(MESSAGE.name in capture.output[0])

    async def test_filtered(self):
        with self.assertLogs(level="INFO") as capture:
            try:
                os.environ[FASTIOT_NATS_LOGGER_FILTER_FIELD] = 'value'
                os.environ[FASTIOT_NATS_LOGGER_FILTER_VALUE] = '25'
                await self._start_service()
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
