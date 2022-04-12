import asyncio
from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine

from fastiot.core.subject import Subject


class Stream(ABC):
    @abstractmethod
    async def update_beat(self, beat: Any):
        pass

    @abstractmethod
    async def close(self):
        pass


class StreamImpl(Stream):
    def __init__(self, on_beat: Callable[..., Any]):
        self._beat_task = asyncio.create_task(self._run())

    async def _run(self):
        pass

    async def update_beat(self, beat: Any):
        pass

    async def close(self):
        pass


class BrokerConnection(ABC):
    @abstractmethod
    async def subscribe(self, subject: Subject, cb: Callable[..., Coroutine]):
        pass

    @abstractmethod
    async def publish(self, subject: Subject, msg: Any):
        pass

    @abstractmethod
    async def request(self, subject: Subject, msg: Any) -> Any:
        pass

    @abstractmethod
    async def open_stream(self,
                          subject: Subject,
                          beat: Any, cb: Callable[..., Coroutine],
                          on_beat: Callable[..., Any] = None) -> Stream:
        pass


class BrokerConnectionImpl(BrokerConnection):
    async def subscribe(self, subject: Subject, cb: Callable[..., Coroutine]):
        pass

    async def publish(self, subject: Subject, msg: Any):
        pass

    async def request(self, subject: Subject, msg: Any) -> Any:
        pass

    async def open_stream(self, subject: Subject, beat: Any, cb: Callable[..., Coroutine],
                          on_beat: Callable[..., Any] = None) -> Stream:
        pass


