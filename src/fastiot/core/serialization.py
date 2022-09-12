from typing import Type, Union

from ormsgpack import ormsgpack

from fastiot.core.data_models import FastIoTData


def serialize_to_bin(model: Union[FastIoTData, dict]):
    if isinstance(model, FastIoTData):
        return ormsgpack.packb(model, option=ormsgpack.OPT_SERIALIZE_PYDANTIC)
    else:
        return ormsgpack.packb(model)


def serialize_from_bin(model_cls: Union[Type[FastIoTData], Type[dict]], data: bytes):
    unpacked = ormsgpack.unpackb(data)
    if issubclass(model_cls, FastIoTData):
        return model_cls(**unpacked)
    else:
        return unpacked

