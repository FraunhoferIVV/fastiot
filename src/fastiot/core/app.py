import asyncio
from abc import ABCMeta, ABC
from functools import wraps
from typing import List, Dict, Any, Callable

from pydantic import BaseModel

from fastiot.core.broker_connection import BrokerConnection
from fastiot.core.subject import Subject


BROKER_CONNECTION_KEY = "fastiot-broker"


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


class _SubjectWrapper(BaseModel):
    fn: Callable
    subject: Subject


class _WrappedLoop(BaseModel):
    fn: Callable
    inject: List[str]



def subscribe(subject: Subject):
    if subject.reply_cls is not None:
        raise ValueError("Expected subject to have no reply_cls for subscription mode")

    def subscribe_wrapper_fn(fn):
        fn.__fastiot_subject = subject
        return fn
    return subscribe_wrapper_fn


def reply(subject: Subject):
    if subject.reply_cls is None:
        raise ValueError("Expected subject to have a reply_cls for reply mode")
    if subject.stream_mode:
        raise ValueError("Expected subject to have stream mode disabled for reply mode")

    def subscribe_wrapper_fn(fn):
        fn.__fastiot_subject = subject
        return fn
    return subscribe_wrapper_fn


def stream(subject: Subject):
    if subject.reply_cls is None:
        raise ValueError("Expected subject to have a reply_cls for stream mode")
    if subject.stream_mode is False:
        raise ValueError("Expected subject to have stream mode enabled for stream mode")

    def subscribe_wrapper_fn(fn):
        fn.__fastiot_subject = subject
        return fn

    return subscribe_wrapper_fn


def loop(fn):
    fn.__fastiot_is_loop = True
    return fn


class FastIoTAppMeta(ABCMeta):
    def __new__(cls, name, bases, dct):
        cls.


class FastIoTApp(metaclass=FastIoTAppMeta, ABC):
    def __init__(self, broker_connection: BrokerConnection):
        pass

    def implement(self, subject: Subject, inject: List[str] = None):
        def fn_wrapper(fn):
            if asyncio.iscoroutinefunction(fn) is False:
                raise TypeError("Expected a coroutine function")

            self._implementations.append(_WrappedImplementation(
                fn=fn,
                subject=subject,
                inject=inject
            ))
        return fn_wrapper

    def loop(self, inject: List[str] = None, name: str = None):
        def fn_wrapper(fn):
            if asyncio.iscoroutinefunction(fn) is False:
                raise TypeError("Expected a coroutine function")

            self._loops.append(_WrappedLoop(
                fn=fn,
                inject=inject
            ))
        return fn_wrapper

    def run(self, provide: Dict[str, Any]):
        if self._broker_connection_key not in provide:
            raise ValueError(f"Expected {self._broker_connection_key} to be included in provide.")

        task_runners = []

    def test_client(self, provide: Dict[str, Any]) -> FastIoTAppClient:
        pass
