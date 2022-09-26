import asyncio
import signal
from typing import List

from fastiot import logging
from fastiot.core.broker_connection import BrokerConnection, NatsBrokerConnection, Subscription
from fastiot.env import env_basic
from fastiot.exceptions.exceptions import ShutdownRequestedInterruption


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

        :param kwargs: kwargs will be passed to class constructor.
        """

        async def run_main():
            app = None
            async def closed_cb():
                # We want to request service shutdown if connection closes
                nonlocal app
                if app is not None:
                    await app.request_shutdown("Lost connection to broker")

            broker_connection = await NatsBrokerConnection.connect(
                closed_cb=closed_cb
            )
            try:
                app = cls(broker_connection=broker_connection, **kwargs)
                await app.run()
            finally:
                await broker_connection.close()

        asyncio.run(run_main())

    def __init__(self, broker_connection: BrokerConnection, **kwargs):
        super().__init__(**kwargs)
        self.broker_connection = broker_connection
        self._shutdown_event = asyncio.Event()

        self._subscription_fns = []
        self._reply_subscription_fns = []
        self._loop_fns = []
        self._tasks: List[asyncio.Task] = []
        self._subs: List[Subscription] = []
        self.service_id: str = env_basic.service_id  # Use to separate different services instantiated
        self._logger = logging

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

    async def _start(self):
        """ Optionally overwrite this method to run any async start commands like ``await self._server.start()``` """

    async def _stop(self):
        """ Optionally overwrite this method to run any async stop commands like ``await self._server.stop()``` """


    def run_task(self, coro):
        """
        Creates an asyncio-Task which is managed by this class. If the execution
        of the coroutine raises an exception, they are logged and a service
        shutdown is requested. If the task terminates reguarly, it is dropped
        and the module continuous to run.

        The task is awaited after _stop() has been called.
        """
        self._tasks.append(
            asyncio.create_task(self._exec_task(coro=coro))
        )

    async def _exec_task(self, coro):
        err = None
        try:
            await coro
        except Exception as e:
            self._logger.exception("Uncaught exception raised inside task")
            err = e
        if err:
            await self.request_shutdown("Task failed with an exception")

    async def wait_for_shutdown(self, timeout: float = 0.0) -> bool:
        """
        Method to wait for service shutdown. This is helpfull if you have a loop
        running forever till the service needs to shutdown.

        Shutdown may occur when some other parts of the service fail like
        database connection or broker connection.

        Per default, it will wait indefinetly, but you can specify a timeout. If
        timeout exceeds, it will not raise a timeout error, but instead return
        false. Otherwise it will return true.

        Example:
        >>> while await self.wait_for_shutdown(1.0) is False:
        >>>     print("Still running...")

        :param timeout: Specify a time you want to wait for the shutdown. A
                        value of 0.0 (default) will wait indefinetly.
        :result Return true if shutdown is requested, false if timeout occured.
        """
        if timeout < 0:
            raise ValueError("Timeout must be greater or equal zero")

        if timeout == 0:
            await self._shutdown_event.wait()
            return True

        result = True
        try:
            await asyncio.wait_for(
                self._shutdown_event.wait(),
                timeout=timeout
            )
        except TimeoutError:
            result = False
        return result

    async def run_coro(self, coro):
        """
        Waits for coro or raises ShutdownRequestedInterruption if shutdown is
        requested.

        :param coro: The coroutine to wait for
        :returns The result of the coroutine
        """
        async def _wait_and_raise_interruption():
            await self.wait_for_shutdown()
            raise ShutdownRequestedInterruption()

        for c in asyncio.as_completed([coro, _wait_and_raise_interruption()]):
            return await c

    async def __aenter__(self):
        self._shutdown_event.clear()
        await self._start()
        await self._start_service_annotations()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.request_shutdown()
        await self._stop_service_annotations()
        await self._stop()
        return False

    async def run(self):
        self._shutdown_event.clear()
        loop = asyncio.get_running_loop()

        def handler(signum, _):
            nonlocal loop
            if signum == signal.SIGTERM:
                asyncio.run_coroutine_threadsafe(self.request_shutdown(), loop=loop)

        signal.signal(signal.SIGTERM, handler)

        await self._start()
        await self._start_service_annotations()

        await self.wait_for_shutdown()

        await self._stop_service_annotations()
        await self._stop()

    async def request_shutdown(self, reason: str = ''):
        """ Sets the shutdown request for all loops and tasks in the service to stop """
        if self._shutdown_event.is_set() is False and reason:
            self._logger.info(f"Initial shutdown requested with reason: {reason}")
        self._shutdown_event.set()

    async def _start_service_annotations(self):
        for loop_fn in self._loop_fns:
            self.run_task(self._loop_task_cb(loop_fn=loop_fn))

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

    async def _loop_task_cb(self, loop_fn):
        while True:
            awaitable = await loop_fn()
            await self.run_coro(awaitable)

    async def _stop_service_annotations(self):
        for sub in self._subs:
            await sub.unsubscribe()
        await asyncio.gather(*self._tasks, *[sub.unsubscribe() for sub in self._subs], return_exceptions=True)
        self._subs = []
        self._tasks = []
