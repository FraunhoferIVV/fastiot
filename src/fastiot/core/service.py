import asyncio
import signal
from asyncio import CancelledError
from typing import List, Dict, Any

from fastiot.core.broker_connection import BrokerConnection, NatsBrokerConnectionImpl


class FastIoTAppClient:

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def open(self):
        pass

    async def close(self):
        pass

    async def call_loop(self, name: str):
        pass


class FastIoTService:
    @classmethod
    def main(cls, **kwargs):
        async def run_main():
            broker_connection = await NatsBrokerConnectionImpl.connect()
            try:
                app = cls(broker_connection=broker_connection, **kwargs)
                await app.run()
            finally:
                await broker_connection.close()

        asyncio.run(run_main())

    def __init__(self, broker_connection: BrokerConnection, **kwargs):
        super().__init__(**kwargs)
        self.broker_connection = broker_connection

        self._subscription_fns = []
        self._loop_fns = []
        self._tasks: List[asyncio.Task] = []
        self._subs = []
        self.service_id = None  # Use to separate between different services instantiated

        for name in dir(self):
            if name.startswith('__'):
                continue
            attr = self.__getattribute__(name)
            if hasattr(attr, '_fastiot_is_loop'):
                self._loop_fns.append(attr)
            if hasattr(attr, '_fastiot_subject'):
                self._subscription_fns.append(attr)

    async def run(self):
        loop = asyncio.get_running_loop()
        shutdown_requested = asyncio.Event()

        async def _set_shutdown():
            nonlocal shutdown_requested
            await self._stop()
            shutdown_requested.set()

        def handler(signum, _):
            nonlocal loop, _set_shutdown
            if signum == signal.SIGTERM:
                asyncio.run_coroutine_threadsafe(_set_shutdown(), loop=loop)

        signal.signal(signal.SIGTERM, handler)

        await self._start()

        for loop_fn in self._loop_fns:
            self._tasks.append(
                asyncio.create_task(self._run_loop(loop_fn=loop_fn))
            )

        for subscription_fn in self._subscription_fns:
            sub = await self.broker_connection.subscribe(
                subject=subscription_fn._fastiot_subject,
                cb=subscription_fn
            )
            self._subs.append(sub)

        await shutdown_requested.wait()

        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, *[sub.unsubscribe() for sub in self._subs], return_exceptions=True)
        self._tasks = []
        self._subs = []

    async def _run_loop(self, loop_fn):
        try:
            while True:
                awaitable = await asyncio.shield(loop_fn())
                await awaitable
        except CancelledError:
            pass

    async def _start(self):
        """ Overwrite this method to run any async start commands like ``await self._server.start()``` """

    async def _stop(self):
        """ Overwrite this method to run any async stop commands like ``await self._server.stop()``` """

    async def test_client(self, provide: Dict[str, Any]) -> FastIoTAppClient:
        pass
