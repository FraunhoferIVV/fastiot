from typing import Type

from ormsgpack import ormsgpack
from pydantic.main import BaseModel


def model_to_bin(model: BaseModel):
    return ormsgpack.packb(model, option=ormsgpack.OPT_SERIALIZE_PYDANTIC)


def model_from_bin(cls: Type[BaseModel], data: bytes):
    unpacked = ormsgpack.unpackb(data)
    return cls(**unpacked)
