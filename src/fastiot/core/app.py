import asyncio
from dataclasses import dataclass
from functools import wraps
from typing import List, Dict, Any, Callable

from fastiot.core.subject import Subject


BROKER_CONNECTION_SERVICE_KEY = "fastiot-broker"


class FastIoTAppClient:
    async def call(self):
        pass


@dataclass
class _WrappedImplementation:
    fn: Callable
    subject: Subject
    inject: List[str]


@dataclass
class _WrappedLoop:
    fn: Callable
    inject: List[str]


class FastIoTApp:
    def __init__(self, broker_connection_service_key: str = BROKER_CONNECTION_SERVICE_KEY):
        self._broker_connection_service_key = broker_connection_service_key
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

    def loop(self, inject: List[str] = None):
        def fn_wrapper(fn):
            if asyncio.iscoroutinefunction(fn) is False:
                raise TypeError("Expected a coroutine function")

            self._loops.append(_WrappedLoop(
                fn=fn,
                inject=inject
            ))
        return fn_wrapper

    async def run(self, provide: Dict[str, Any]):
        task_runners = []

    def test_client(self) -> FastIoTAppClient:
        pass
