import asyncio
import unittest

from fastiot.core import FastIoTService, loop
from fastiot.core.broker_connection import BrokerConnectionDummy


class LoopingFastIoTTestService(FastIoTService):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.crash = False
        self.counter = 0

    def set_crash_parameter(self, param):
        self.crash = param

    @loop
    async def looping_function(self):
        if self.crash:
            raise RuntimeError("Looping crashed")
        if self.counter < 2:
            self._logger.info("Loop Running: %i", self.counter)
        self.counter += 1
        return asyncio.sleep(0.01)

    @loop
    async def ever_looping_function(self):
        return asyncio.sleep(10)


class TestPublishSubscribe(unittest.IsolatedAsyncioTestCase):

    async def test_regular_output(self):
        with self.assertLogs(level="INFO") as capture:
            async with LoopingFastIoTTestService(broker_connection=BrokerConnectionDummy()) as service:
                await asyncio.sleep(0.03)
                self.assertEqual(2, sum("Loop Running" in t for t in capture.output))
                service.request_shutdown()

    async def test_crash_in_loop(self):
        async with LoopingFastIoTTestService(broker_connection=BrokerConnectionDummy()) as service:
            service.set_crash_parameter(True)
            shutdown_requested = await service.wait_for_shutdown(timeout=0.25)
            self.assertTrue(shutdown_requested)
