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

    async def test_regular_output_aenter(self):
        with self.assertLogs(level="INFO") as capture:
            async with LoopingFastIoTTestService(broker_connection=BrokerConnectionDummy()) as service:
                shutdown_requested = await service.wait_for_shutdown(timeout=0.01)
                self.assertFalse(shutdown_requested)
                await asyncio.sleep(0.03)
                self.assertEqual(2, sum("Loop Running" in t for t in capture.output))
                await service.request_shutdown()

    async def test_crash_in_loop_aenter(self):
        async with LoopingFastIoTTestService(broker_connection=BrokerConnectionDummy()) as service:
            shutdown_requested = await service.wait_for_shutdown(timeout=0.01)
            self.assertFalse(shutdown_requested)

            service.set_crash_parameter(True)

            shutdown_requested = await service.wait_for_shutdown(timeout=0.25)
            self.assertTrue(shutdown_requested)

    async def test_regular_output(self):
        service = LoopingFastIoTTestService(broker_connection=BrokerConnectionDummy())
        with self.assertLogs(level="INFO") as capture:
            service_task = asyncio.create_task(service.run())
            await asyncio.sleep(0.05)

            shutdown_requested = await service.wait_for_shutdown(timeout=0.01)
            self.assertFalse(shutdown_requested)

            self.assertEqual(2, sum("Loop Running" in t for t in capture.output))
            await service.request_shutdown()

        shutdown_requested = await service.wait_for_shutdown(timeout=10)
        self.assertTrue(shutdown_requested)
        service_task.cancel()

    async def test_crash_in_loop(self):
        service = LoopingFastIoTTestService(broker_connection=BrokerConnectionDummy())
        service_task = asyncio.create_task(service.run())
        shutdown_requested = await service.wait_for_shutdown(timeout=0.01)
        self.assertFalse(shutdown_requested)

        service.set_crash_parameter(True)

        shutdown_requested = await service.wait_for_shutdown(timeout=10)
        self.assertTrue(shutdown_requested)

        service_task.cancel()


if __name__ == '__main__':
    unittest.main()
