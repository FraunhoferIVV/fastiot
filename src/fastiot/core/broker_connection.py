import asyncio
import concurrent.futures
import threading
import time
from abc import ABC, abstractmethod
from asyncio import get_running_loop
from inspect import signature
from typing import Any, Callable, Coroutine, Generic, List, NewType, Optional, TypeVar, Union, AsyncIterator

import nats
from nats.aio.client import Client as BrokerClient
from nats.aio.subscription import Subscription as BrokerSubscription
from nats.aio.msg import Msg as BrokerMsg
from pydantic import BaseModel

from fastiot.core.serialization import serialize_from_bin, serialize_to_bin
from fastiot.core.data_models import MsgCls, Subject, ReplySubject
from fastiot.env import env_broker


# passes MsgCls or str (subject_name) and MsgCls into callback
SubscriptionCallback = Callable[..., Coroutine[None, None, None]]
SubscriptionReplyCallback = Callable[..., Coroutine[None, None, MsgCls]]


class Subscription(ABC):
    @abstractmethod
    async def unsubscribe(self):
        """
        Cancels the subscription
        """

    @abstractmethod
    def check_pending_error(self):
        """
        Checks if an error is pending and raises it.
        """

    @abstractmethod
    async def raise_pending_error(self):
        """
        Waits for a pending error and raises it. Useful for testing.
        """


class SubscriptionBaseImpl(Subscription, ABC):
    def __init__(self,
                 max_pending_errors: int = 1000,
                 **kwargs):
        super().__init__(**kwargs)
        self._subscription = None
        self._pending_errors = asyncio.Queue(maxsize=max_pending_errors)

    def _set_subscription(self, subscription: BrokerSubscription):
        self._subscription = subscription

    async def unsubscribe(self):
        if self._subscription is None:
            raise RuntimeError("Expected a subscription object")
        await self._subscription.unsubscribe()


    def check_pending_error(self):
        if self._pending_errors.empty() is False:
            next_error = self._pending_errors.get_nowait()
            self._pending_errors.task_done()
            raise next_error

    async def raise_pending_error(self):
        next_error = await self._pending_errors.get()
        raise next_error


class SubscriptionSubjectImpl(SubscriptionBaseImpl):
    def __init__(self,
                 subject: Subject,
                 on_msg_cb: SubscriptionCallback,
                 **kwargs):
        super().__init__(**kwargs)
        self._subject = subject
        self._on_msg_cb = on_msg_cb
        self._num_cb_params = len(signature(on_msg_cb).parameters)

    async def _received_msg_cb(self, nats_msg: BrokerMsg):
        try:
            msg = serialize_from_bin(self._subject.msg_cls, nats_msg.data)
            if self._num_cb_params == 1:
                result = await self._on_msg_cb(msg)
            elif self._num_cb_params == 2:
                result = await self._on_msg_cb(nats_msg.subject, msg)
            else:
                raise NotImplementedError("Callbacks with more then two params are not intended yet.")

            if result is not None:
                raise TypeError(
                    f"Callbacks for subscriptions must return None. "
                    f"Got object of type {type(result)} instead. "
                    f"Maybe you need to use request pattern, e.g. @reply instead of @subscribe?"
                )

        except Exception as e:
            if self._pending_errors.full() is False:
                self._pending_errors.put_nowait(e)
        finally:
            pass


class SubscriptionReplySubjectImpl(SubscriptionBaseImpl):
    def __init__(self,
                 subject: ReplySubject,
                 on_msg_cb: SubscriptionReplyCallback,
                 send_reply_fn: Callable[[Subject, MsgCls], Coroutine[None, None, None]]):
        self._subject = subject
        self._on_msg_cb = on_msg_cb
        self._num_cb_params = len(signature(on_msg_cb).parameters)
        self._send_reply_fn = send_reply_fn
        self._subscription = None

        cb_signature = signature(self._on_msg_cb)
        self._cb_with_subject = len(cb_signature.parameters) == 2

    async def _received_msg_cb(self, nats_msg: BrokerMsg):
        try:
            msg = serialize_from_bin(self._subject.msg_cls, nats_msg.data)
            if self._num_cb_params == 1:
                reply_msg = await self._on_msg_cb(msg)
            elif self._num_cb_params == 2:
                reply_msg = await self._on_msg_cb(nats_msg.subject, msg)
            else:
                raise NotImplementedError("Callbacks with more then two params are not intended yet.")

            if not isinstance(reply_msg, self._subject.reply_cls):
                raise TypeError(f"Callback has not returned correct type: Expected type {self._subject.reply_cls}, "
                                f"got {type(msg)}")

            reply_subject = Subject(
                name=nats_msg.reply,
                msg_cls=self._subject.reply_cls
            )
            await self._send_reply_fn(reply_subject, reply_msg)
        except Exception as e:
            if self._pending_errors.full() is False:
                self._pending_errors.put_nowait(e)
        finally:
            pass


class BrokerConnection(ABC):

    def __init__(self):
        self._loop_mutex = threading.RLock()
        self._loop = None

    @abstractmethod
    async def subscribe(self,
                        subject: Subject,
                        cb: Callable[[BaseModel], Union[Coroutine, AsyncIterator]]) -> Subscription:
        pass

    async def subscribe_msg_queue(self,
                                  subject: Subject,
                                  msg_queue: asyncio.Queue) -> Subscription:

        async def cb(msg):
            nonlocal msg_queue
            await msg_queue.put(msg)

        return await self.subscribe(subject=subject, cb=cb)

    @abstractmethod
    async def send(self, subject: Subject, msg: BaseModel, reply: Subject = None):
        pass

    async def publish(self, subject: Subject, msg: Any):
        if subject.reply_cls is not None:
            raise ValueError("Publish only allowed for empty reply_cls")
        await self.send(subject=subject, msg=msg)

    async def request(self, subject: ReplySubject, msg: Any, timeout: float = env_broker.default_timeout) -> Any:
        inbox = subject.make_generic_reply_inbox()
        msg_queue = asyncio.Queue()
        sub = await self.subscribe_msg_queue(subject=inbox, msg_queue=msg_queue)
        try:
            await self.send(subject=subject, msg=msg, reply=inbox)
            result = await asyncio.wait_for(msg_queue.get(), timeout=timeout)
        finally:
            await sub.unsubscribe()
        return result

    def run_threadsafe_nowait(self, coro: Coroutine) -> concurrent.futures.Future:
        """
        Runs a coroutine on nats client's event loop. This method is thread-safe. It can be useful if you want to
        interact with the broker from another thread. You have to make sure connect(...) has been called first.

        :param coro: The coroutine to run thread-safe on nats client's event loop, for example
                     'nats_client.publish(...)'
        """
        with self._loop_mutex:
            if not self._loop:
                raise RuntimeError("No event loop has been started. Cannot send data in thread safe mode.")

            return asyncio.run_coroutine_threadsafe(coro=coro, loop=self._loop)

    def run_threadsafe(self, coro: Coroutine, timeout_thread_waiting: float = None) -> Any:
        """
        Runs a coroutine on nats client's event loop. This method is thread-safe. It can be useful if you want to
        interact with the broker from another thread. You have to make sure connect(...) has been called first.

        :param coro: The coroutine to run thread-safe on nats client's event loop, for example
                     'nats_client.publish(...)'
        :param timeout_thread_waiting: The number of seconds to wait for the result to be done. Raises
                                       concurrent.futures.TimeoutError if timeout exceeds. A value None means wait
                                       forever.
        :return: Returns the result of the coroutine or if the coroutine raised an exception, it is reraised.
        """
        future = self.run_threadsafe_nowait(coro=coro)
        return future.result(timeout=timeout_thread_waiting)

    def publish_sync(self,
                     subject: Subject,
                     msg: Any = None,
                     timeout_thread_waiting: float = None) -> bool:
        """
        Publishes a message for a subject. This method is thread-safe. Under the hood, it uses run_threadsafe.

        :param subject: The subject info to publish to.
        :param msg: The message.
        :param timeout_thread_waiting: The timeout.
        :return True when method finished successfully
        """
        return self.run_threadsafe(
            coro=self.publish(subject=subject, msg=msg),
            timeout_thread_waiting=timeout_thread_waiting
        )

    def publish_sync_nowait(self,
                            subject: Subject,
                            msg: Any = None) -> concurrent.futures.Future:
        """
        Publishes a message for a subject. This method is thread-safe. Under the hood, it uses run_threadsafe_nowait.

        :param subject: The subject info to publish to.
        :param msg: The message.
        :return True when method finished successfully
        """
        return self.run_threadsafe_nowait(
            coro=self.publish(subject=subject, msg=msg)
        )

    def request_sync(self,
                     subject: ReplySubject,
                     msg: Any = None,
                     timeout: float = env_broker.default_timeout,
                     timeout_thread_waiting: Optional[float] = None) -> Any:
        """
        Performs a request on the subject. This method is thread-safe. Under the hood, it uses run_threadsafe.

        :param subject: The subject info to publish the request.
        :param msg: The request message.
        :param timeout: The timeout for the broker call.
        :param timeout_thread_waiting: The timeout for the thread waiting.
        :return The requested message.
        """
        return self.run_threadsafe(
            coro=self.request(subject=subject, msg=msg, timeout=timeout),
            timeout_thread_waiting=timeout_thread_waiting
        )


class NatsBrokerConnectionImpl(BrokerConnection):

    @classmethod
    async def connect(cls) -> "NatsBrokerConnectionImpl":
        client = await nats.connect(f"nats://{env_broker.host}:{env_broker.port}")
        return cls(
            client=client
        )

    def __init__(self, client: BrokerClient):
        super().__init__()
        self._client = client
        self._loop = get_running_loop()

    async def close(self):
        await self._client.close()

    async def subscribe(self,
                        subject: Subject,
                        cb: Optional[Callable[[BaseModel], Union[Coroutine, AsyncIterator]]],
                        sublist: Optional[List[Subscription]] = None) -> Subscription:
        impl = SubscriptionImpl(
            subject=subject,
            on_msg_cb=cb,
            send_reply_fn=self.send
        )
        subscription = await self._client.subscribe(
            subject=subject.name,
            cb=impl._received_msg_cb
        )
        impl._set_subscription(subscription=subscription)
        return impl

    async def send(self, subject: Subject, msg: BaseModel, reply: Optional[Subject] = None):
        payload = model_to_bin(msg)
        reply_str = '' if reply is None else reply.name
        await self._client.publish(
            subject=subject.name,
            payload=payload,
            reply=reply_str
        )


class BrokerConnectionTestImpl(BrokerConnection):

    def __init__(self):
        super().__init__()
        self._sublist = []

    @abstractmethod
    async def subscribe(self, subject: Subject, cb: Callable[..., Coroutine]) -> Subscription:
        pass

    @abstractmethod
    async def send(self, subject: Subject, msg: BaseModel, reply: Subject = None):
        pass
