import asyncio
from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine, Dict, Union, Generator, AsyncIterator

from nats.aio.client import Client
from ormsgpack import ormsgpack
from pydantic.main import BaseModel

from fastiot.core.serialization import model_from_bin
from fastiot.core.subject import Subject
from fastiot.env import fastiot_broker_env


class Subscription(ABC):
    pass


class SubscriptionImpl(Subscription):
    def __init__(self,
                 subject: Subject,
                 on_msg_cb: Callable[[BaseModel], Union[Coroutine, AsyncIterator]],
                 send_reply_fn: Callable[[str, BaseModel], Coroutine],
                 max_pending_errors: int = 1000):
        self._subject = subject
        self._on_msg_cb = on_msg_cb
        self._send_reply_fn = send_reply_fn
        self._ssid = None
        self._current_stream_tasks: Dict[str, asyncio.Task] = {}
        self._pending_errors = asyncio.Queue(maxsize=max_pending_errors)

    async def received_msg_cb(self, nats_msg):
        try:
            data = model_from_bin(self._subject.msg_cls, nats_msg.data)
            obj = self._subject.msg_cls(**data)

            if self._subject.reply_cls is None:
                await self._on_msg_cb(obj)
            elif self._subject.stream_mode is False:
                ans = await self._on_msg_cb(obj)
                if isinstance(ans, self._subject.reply_cls):
                    raise TypeError(f"Callback has not returned correct type: Expected type {self._subject.reply_cls}, "
                                    f"got {type(ans)}")
                await self._send_reply_fn(nats_msg.reply, ans)
            else:
                generator = self._on_msg_cb(obj)
                while True:
                    ans = await generator.__anext__()
                    if isinstance(ans, self._subject.reply_cls):
                        raise TypeError(f"Callback has not returned correct type: Expected type {self._subject.reply_cls}, "
                                        f"got {type(ans)}")
                    await self._send_reply_fn(nats_msg.reply, ans)
        finally:
            pass


class BrokerConnection(ABC):
    @abstractmethod
    async def subscribe(self, subject: Subject, msg_cls: Any, cb: Callable[..., Coroutine]) -> Subscription:
        pass

    @abstractmethod
    async def unsubscribe(self, subscription: Subscription):
        pass

    @abstractmethod
    async def send(self, msg: Any, to: Subject, reply_to: Subject = None):
        pass

    async def subscribe_msg_queue(self, subject: Subject, msg_cls: Any, msg_queue: asyncio.Queue) -> Subscription:
        pass

    async def publish(self, subject: Subject, msg: Any):
        await self.send(msg=msg, subject=subject)

    async def request(self, subject: Subject, msg: Any) -> Any:
        pass

    async def beat(self, subject: Subject, beat: Any):
        if subject.stream_mode is False:
            raise ValueError("")
        pass


class BrokerConnectionImpl(BrokerConnection):

    @classmethod
    def connect(cls):
        pass

    def __init__(self, client: Client):
        pass

    def close(self):
        pass

    @abstractmethod
    async def subscribe(self, subject: Subject, msg_cls: Any, cb: Callable[..., Coroutine]) -> Subscription:
        pass

    @abstractmethod
    async def unsubscribe(self, subscription: Subscription):
        pass

    @abstractmethod
    async def send(self, msg: Any, to: Subject, reply_to: Subject = None):
        pass


class BrokerConnectionTestImpl(BrokerConnection):

    def __init__(self):
        self._sublist = []

    @abstractmethod
    async def subscribe(self, subject: Subject, msg_cls: Any, cb: Callable[..., Coroutine]) -> Subscription:
        pass

    @abstractmethod
    async def unsubscribe(self, subscription: Subscription):
        pass

    @abstractmethod
    async def send(self, msg: Any, to: Subject, reply_to: Subject = None):
        pass
