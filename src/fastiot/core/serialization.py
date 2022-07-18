from typing import Type, Union

from ormsgpack import ormsgpack
from pydantic.main import BaseModel

from fastiot.core.data_models import FastIoTData


def model_to_bin(model: BaseModel):
    return ormsgpack.packb(model, option=ormsgpack.OPT_SERIALIZE_PYDANTIC)


def model_from_bin(cls: Union[Type[Union[BaseModel, FastIoTData]], dict], data: bytes):
    unpacked = ormsgpack.unpackb(data)
    if cls == dict:
        return unpacked
    return cls(**unpacked)
