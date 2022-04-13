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


class _WrappedImplementation(BaseModel):
    fn: Callable
    subject: Subject
    inject: List[str]


class _WrappedLoop(BaseModel):
    fn: Callable
    inject: List[str]



def subscribe(fn):
    pass


def reply(fn):
    pass


def stream(fn):
    pass


class FastIoTAppMeta(ABCMeta):
    def __new__(cls, name, bases, dct):
        cls.


class FastIoTApp(metaclass=FastIoTAppMeta, ABC):
    def __init__(self, broker_connection: BrokerConnection):
        self._implementations: List[_WrappedImplementation] = []
        self._loops: List[_WrappedLoop] = []

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
