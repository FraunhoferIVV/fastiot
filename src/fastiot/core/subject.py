from abc import ABC
from dataclasses import dataclass
from typing import Type, Any


@dataclass
class Subject(ABC):
    name: str
    msg_cls: Type[Any]
    resp_cls: Type[Any] = None
    stream_cls: Type[Any] = None
