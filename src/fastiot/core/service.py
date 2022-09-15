import asyncio
import logging.config
import signal
from asyncio import CancelledError
from typing import List

from fastiot.core.broker_connection import BrokerConnection, NatsBrokerConnection
from fastiot.env import env_basic
from fastiot.helpers.log_config import get_log_config


class FastIoTService:
    """
    This is the most base class for all FastIoT Services. Your service must inherit from this class for everything to
    work.
    """
    @classmethod
    def main(cls, **kwargs):
        """
        Entrypoint of the class; this is the method to be started using e.g. a :file:`run.py` like generated when
        creating a new service. Do not overwrite, unless you know exactly what you are doing.
        """
        logging.config.dictConfig(get_log_config(env_basic.log_level_no))

        async def run_main():
            broker_connection = await NatsBrokerConnection.connect()
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
        self._reply_subscription_fns = []
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
            if hasattr(attr, '_fastiot_reply_subject'):
                self._reply_subscription_fns.append(attr)

    @property
    def shutdown_requested(self) -> asyncio.Event:
        """
        Method to check, if the service is shutting down. This is helpfull if you have a loop running forever till the
        service needs to shutdown.
        Shutdown may occur when some other parts of the service fail like database connection, broker connection, ….

        Example:
        >>> while not self._shutdown_requested():
        >>>     print("Still running…")
        >>>     asyncio.sleep(1)
        """
        if self._shutdown_requested is None:
            self._shutdown_requested = asyncio.Event()
        return self._shutdown_requested

    async def __aenter__(self):
        self.shutdown_requested.clear()
        await self._start()
        await self._start_service_annotations()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._stop()
        return False

    async def run(self):
        self.shutdown_requested.clear()
        loop = asyncio.get_running_loop()

        def handler(signum, _):
            nonlocal loop
            if signum == signal.SIGTERM:
                asyncio.run_coroutine_threadsafe(self.request_shutdown(), loop=loop)

        signal.signal(signal.SIGTERM, handler)

        await self._start()
        await self._start_service_annotations()

        await self.shutdown_requested.wait()

        await self._stop_service_annotations()
        await self._stop()

    async def request_shutdown(self):
        """ Sets the shutdown request for all loops and tasks in the service to stop """
        self.shutdown_requested.set()

    async def _start_service_annotations(self):
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

        for subscription_fn in self._reply_subscription_fns:
            sub = await self.broker_connection.subscribe_reply_cb(
                subject=subscription_fn._fastiot_reply_subject,
                cb=subscription_fn
            )
            self._subs.append(sub)

    async def _stop_service_annotations(self):
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
        """ Optionally overwrite this method to run any async start commands like ``await self._server.start()``` """

    async def _stop(self):
        """ Optionally overwrite this method to run any async stop commands like ``await self._server.stop()``` """
