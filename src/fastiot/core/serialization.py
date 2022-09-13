from typing import Type, Union

from ormsgpack import ormsgpack

from fastiot.core.data_models import FastIoTData, Msg, MsgCls


def serialize_to_bin(msg_cls: MsgCls, msg: Msg) -> bytes:
    """
    Serializes a msg to binary. It also applies some basic type checks.
    """
    if issubclass(msg_cls, FastIoTData):
        if not isinstance(msg, msg_cls):
            raise TypeError(
                f"Expected msg to be of type '{msg_cls}', but it is instead "
                f"of type '{type(msg)}' instead."
            )
        return ormsgpack.packb(msg, option=ormsgpack.OPT_SERIALIZE_PYDANTIC)
    else:
        return ormsgpack.packb(msg)


def serialize_from_bin(msg_cls: MsgCls, data: Msg):
    """
    Serializes a msg from binary.
    """
    unpacked = ormsgpack.unpackb(data)
    if issubclass(msg_cls, FastIoTData):
        return msg_cls(**unpacked)
    else:
        return unpacked

