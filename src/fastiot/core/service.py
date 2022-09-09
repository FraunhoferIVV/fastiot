import asyncio
import signal
from asyncio import CancelledError
from typing import List, Dict, Any

from fastiot.core.broker_connection import BrokerConnection, NatsBrokerConnectionImpl


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
        self._shutdown_requested = None

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

    @property
    def shutdown_requested(self) -> asyncio.Event:
        if self._shutdown_requested is None:
            self._shutdown_requested = asyncio.Event()
        return self._shutdown_requested

    async def run(self):
        self.shutdown_requested.clear()
        loop = asyncio.get_running_loop()

        async def _set_shutdown():
            await self._stop()
            self.shutdown_requested.set()

        def handler(signum, _):
            nonlocal _set_shutdown, loop
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

        await self.shutdown_requested.wait()

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

