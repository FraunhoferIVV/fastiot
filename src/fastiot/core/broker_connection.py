import asyncio
import concurrent.futures
import threading
from abc import ABC, abstractmethod
from asyncio import get_running_loop
from inspect import signature
from typing import Any, Callable, Coroutine, Generic, List, NewType, Optional, TypeVar, Union, AsyncIterator

from nats.aio.client import Client as BrokerClient, Callback as BrokerCallback
from nats.aio.subscription import Subscription as BrokerSubscription
from nats.aio.msg import Msg as NatsBrokerMsg

from fastiot.core.serialization import serialize_from_bin, serialize_to_bin
from fastiot.core.data_models import Msg, Subject, ReplySubject
from fastiot.env import env_broker


# passes MsgCls or str (subject_name) and MsgCls into callback
SubscriptionCallback = Callable[..., Coroutine[None, None, None]]
SubscriptionReplyCallback = Callable[..., Coroutine[None, None, Msg]]


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


class NatsBrokerSubscription(Subscription):
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


class NatsBrokerSubscriptionSubject(NatsBrokerSubscription):
    def __init__(self,
                 subject: Subject,
                 cb: SubscriptionCallback,
                 **kwargs):
        super().__init__(**kwargs)
        self._subject = subject
        self._cb = cb
        self._num_cb_params = len(signature(cb).parameters)

    async def received_nats_msg_cb(self, nats_msg: NatsBrokerMsg):
        try:
            msg = serialize_from_bin(self._subject.msg_cls, nats_msg.data)
            if self._num_cb_params == 1:
                result = await self._cb(msg)
            elif self._num_cb_params == 2:
                result = await self._cb(nats_msg.subject, msg)
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


class NatsBrokerSubscriptionReplySubject(NatsBrokerSubscription):
    def __init__(self,
                 subject: ReplySubject,
                 cb: SubscriptionReplyCallback,
                 send_reply_fn: Callable[[Subject, Msg], Coroutine[None, None, None]]):
        self._subject = subject
        self._cb = cb
        self._num_cb_params = len(signature(cb).parameters)
        self._send_reply_fn = send_reply_fn
        self._subscription = None

        cb_signature = signature(self._cb)
        self._cb_with_subject = len(cb_signature.parameters) == 2

    async def received_nats_msg_cb(self, nats_msg: NatsBrokerMsg):
        try:
            msg = serialize_from_bin(self._subject.msg_cls, nats_msg.data)
            if self._num_cb_params == 1:
                reply_msg = await self._cb(msg)
            elif self._num_cb_params == 2:
                reply_msg = await self._cb(nats_msg.subject, msg)
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._loop_mutex = threading.RLock()
        # Try to set loop for synchronous functionality
        try:
            self._loop = asyncio.get_event_loop()
        except RuntimeError:
            self._loop = None

    def _set_loop(self, loop: asyncio.AbstractEventLoop):
        with self._loop_mutex:
            self._loop = loop

    @abstractmethod
    async def subscribe(self,
                        subject: Subject,
                        cb: SubscriptionCallback) -> Subscription:
        """
        Subscribe to a subject.

        :param subject: The subject to subscribe to
        :param cb: The callback which is called when a message is received
        """
        pass

    async def subscribe_msg_queue(self,
                                  subject: Subject,
                                  msg_queue: asyncio.Queue[Msg]) -> Subscription:
        """
        Subscribe to a subject using a message queue instead of a callback.
        Use this if you prefer querying a msg_queue.

        :param subject: The subject to subscribe to
        :param msg_queue: The message queue where received messages are enqueued.
        """
        async def cb(msg):
            nonlocal msg_queue
            await msg_queue.put(msg)
        return await self.subscribe(subject=subject, cb=cb)

    @abstractmethod
    async def subscribe_reply_cb(self,
                                 subject: ReplySubject,
                                 cb: SubscriptionReplyCallback) -> Subscription:
        """
        Subscribe to a reply subject. It is expected that the message will be answered.

        :param subject: The reply subject to subscribe to
        :param cb: The callback which is called when a request is received
        """
        pass

    @abstractmethod
    async def _send(self, subject: Subject, msg: Msg, reply: Optional[Subject] = None):
        """
        Low level method to send msg to broker
        """
        pass

    async def publish(self, subject: Subject, msg: Msg):
        """
        Publishes a message for a subject.

        :param subject: The subject info to publish to.
        :param msg: The message.
        """
        await self._send(subject=subject, msg=msg)

    async def request(self, subject: ReplySubject, msg: Msg, timeout: float = env_broker.default_timeout) -> Msg:
        """
        Send a request on a subject.

        :param subject: The subject used for sending the request.
        :param msg: The request
        :param timeout: The time to wait for an answer. Raises ErrTimeout if no answer is received in time.
        :return The response
        """
        inbox = subject.make_generic_reply_inbox()
        msg_queue = asyncio.Queue()
        sub = await self.subscribe_msg_queue(subject=inbox, msg_queue=msg_queue)
        try:
            await self._send(subject=subject, msg=msg, reply=inbox)
            result = await asyncio.wait_for(msg_queue.get(), timeout=timeout)
        finally:
            await sub.unsubscribe()
        return result

    def run_threadsafe_nowait(self, coro: Coroutine) -> concurrent.futures.Future:
        """
        Runs a coroutine on brokers event loop. This method is thread-safe. It
        can be useful if you want to interact with the broker from another
        thread.

        :param coro: The coroutine to run thread-safe on brokers event loop,
                     for example 'broker_client.publish(...)'
        """
        with self._loop_mutex:
            if not self._loop:
                raise RuntimeError(
                    "No event loop has been detected. Please make sure the "
                    "connection is created in an asyncio context or the loop "
                    "has been set manually."
                )
            return asyncio.run_coroutine_threadsafe(coro=coro, loop=self._loop)

    def run_threadsafe(self, coro: Coroutine, timeout: float = 0.0) -> Any:
        """
        Runs a coroutine on brokers event loop. This method is thread-safe. It
        can be useful if you want to interact with the broker from another
        thread.

        :param coro: The coroutine to run thread-safe on brokers event loop,
                     for example 'broker_client.publish(...)'
        :param timeout: The number of seconds to wait for the result to be done.
                        Raises concurrent.futures.TimeoutError if timeout
                        exceeds. A value of zero means wait forever.
        :return: Returns the result of the coroutine. If the coroutine raised
                 an exception, it is reraised.
        """
        future = self.run_threadsafe_nowait(coro=coro)
        return future.result(timeout=timeout if timeout else None)

    def publish_sync(self,
                     subject: Subject,
                     msg: Msg,
                     timeout: float = 0.0):
        """
        Publishes a message for a subject. This method is thread-safe. Under the
        hood, it uses run_threadsafe.

        :param subject: The subject info to publish to.
        :param msg: The message.
        :param timeout: The timeout.
        """
        return self.run_threadsafe(
            coro=self.publish(subject=subject, msg=msg),
            timeout=timeout
        )

    def publish_sync_nowait(self,
                            subject: Subject,
                            msg: Msg) -> concurrent.futures.Future:
        """
        Publishes a message for a subject. This method is thread-safe. Under the
        hood, it uses run_threadsafe_nowait.

        :param subject: The subject info to publish to.
        :param msg: The message.
        """
        return self.run_threadsafe_nowait(
            coro=self.publish(subject=subject, msg=msg)
        )

    def request_sync(self,
                     subject: ReplySubject,
                     msg: Msg,
                     timeout: float = env_broker.default_timeout) -> Any:
        """
        Performs a request on the subject. This method is thread-safe. Under the
        hood, it uses run_threadsafe.

        Please note, that it will only timeout if the request times out. For
        purposes of simplicity it will wait forever, if the executing thread is
        occupied too much and the request cannot be scheduled.

        :param subject: The subject info to publish the request.
        :param msg: The request message.
        :param timeout: The timeout for the broker call.
        :return The requested message.
        """
        return self.run_threadsafe(
            coro=self.request(subject=subject, msg=msg, timeout=timeout)
        )


class NatsBrokerConnection(BrokerConnection):

    @classmethod
    async def connect(cls,
                      closed_cb: Optional[BrokerCallback] = None
                      ) -> "NatsBrokerConnection":
        """
        Connects a nats instance and returns a nats broker connection.
        """
        client = BrokerClient()
        await client.connect(
            f"nats://{env_broker.host}:{env_broker.port}",
            closed_cb=closed_cb
        )
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
                        cb: SubscriptionCallback,
                        ) -> Subscription:
        result = NatsBrokerSubscriptionSubject(
            subject=subject,
            cb=cb,
        )
        subscription = await self._client.subscribe(
            subject=subject.name,
            cb=result.received_nats_msg_cb
        )
        result._set_subscription(subscription=subscription)
        return result

    async def subscribe_reply_cb(self,
                                 subject: ReplySubject,
                                 cb: SubscriptionReplyCallback) -> Subscription:
        result = NatsBrokerSubscriptionReplySubject(
            subject=subject,
            cb=cb,
            send_reply_fn=self._send
        )
        subscription = await self._client.subscribe(
            subject=subject.name,
            cb=result.received_nats_msg_cb
        )
        result._set_subscription(subscription=subscription)
        return result

    async def _send(self,
                    subject: Subject,
                    msg: Msg,
                    reply: Optional[Subject] = None):
        payload = serialize_to_bin(subject.msg_cls, msg)
        reply_str = '' if reply is None else reply.name
        await self._client.publish(
            subject=subject.name,
            payload=payload,
            reply=reply_str
        )


class SubscriptionDummy(Subscription):
    async def unsubscribe(self):
        pass

    def check_pending_error(self):
        pass

    async def raise_pending_error(self):
        await asyncio.Event().wait()


class BrokerConnectionDummy(BrokerConnection):
    """
    A dummy broker implementation to mock dependencies.
    """

    async def subscribe(self,
                        subject: Subject,
                        cb: SubscriptionCallback) -> Subscription:
        return SubscriptionDummy()

    async def subscribe_reply_cb(self,
                                 subject: ReplySubject,
                                 cb: SubscriptionReplyCallback) -> Subscription:
        return SubscriptionDummy()

    async def _send(self,
                    subject: Subject,
                    msg: Msg,
                    reply: Optional[Subject] = None):
        pass

