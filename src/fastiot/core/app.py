import asyncio
import signal
import threading
from abc import ABCMeta, ABC
from asyncio import CancelledError
from functools import wraps
from typing import List, Dict, Any, Callable

from pydantic import BaseModel

from fastiot.core.broker_connection import BrokerConnection, BrokerConnectionImpl
from fastiot.core.subject import Subject


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


class FastIoTApp:
    @classmethod
    def main(cls, **kwargs):
        async def run_main():
            #broker_connection = await BrokerConnectionImpl.connect()
            broker_connection = None
            try:
                app = cls(broker_connection=broker_connection, **kwargs)
                await app.run()
            finally:
                await broker_connection.close()
        asyncio.run(run_main())

    def __init__(self, broker_connection: BrokerConnection, **kwargs):
        super().__init__(**kwargs)
        self.broker_connection = broker_connection

        self.__subscription_fns = []
        self.__loop_fns = []
        self.__tasks: List[asyncio.Task] = []
        self.__subs = []

        for name in dir(self):
            if name.startswith('__'):
                continue
            attr = self.__getattribute__(name)
            if hasattr(attr, '__fastiot_is_loop'):
                self.__loop_fns.append(attr)
            if hasattr(attr, '__fastiot_subject'):
                self.__subscription_fns.append(attr)

    async def run(self):
        loop = asyncio.get_running_loop()
        shutdown_requested = asyncio.Event()

        async def _set_shutdown():
            nonlocal shutdown_requested
            shutdown_requested.set()

        def handler(signum, frame):
            nonlocal loop, _set_shutdown
            if signum == signal.SIGTERM:
                asyncio.run_coroutine_threadsafe(_set_shutdown(), loop=loop)
        signal.signal(signal.SIGTERM, handler)

        for loop_fn in self.__loop_fns:
            self.__tasks.append(
                asyncio.create_task(self._run_loop(loop_fn=loop_fn))
            )

        for subscription_fn in self.__subscription_fns:
            sub = await self.broker_connection.subscribe(
                subject=subscription_fn.__fastiot_subject,
                cb=subscription_fn
            )
            self.__subs.append(sub)

        await shutdown_requested.wait()

        for task in self.__tasks:
            task.cancel()
        await asyncio.gather(*self.__tasks, *[sub.unsubscribe() for sub in self.__subs], return_exceptions=True)
        self.__tasks = []
        self.__subs = []

    async def _run_loop(self, loop_fn):
        try:
            while True:
                awaitable = await asyncio.shield(loop_fn())
                await awaitable
        except CancelledError:
            pass

    async def test_client(self, provide: Dict[str, Any]) -> FastIoTAppClient:
        pass
