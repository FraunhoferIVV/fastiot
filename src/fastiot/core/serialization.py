import msgpack


from fastiot.core.data_models import FastIoTData, Msg, MsgCls


def serialize_to_bin(msg_cls: MsgCls, msg: Msg) -> bytes:
    """
    Serializes a msg to binary. It also applies some basic type checks.
    Please be careful, msgpack will only serialize python primary data types.
    Data types from numpy for example, cannot be serialized.
    """
    if issubclass(msg_cls, FastIoTData):
        if not isinstance(msg, msg_cls):
            raise TypeError(
                f"Expected msg to be of type '{msg_cls}', but it is instead "
                f"of type '{type(msg)}' instead."
            )
        return msgpack.packb(msg.dict(), datetime=True)

    return msgpack.packb(msg, datetime=True)


def serialize_from_bin(msg_cls: MsgCls, data: bytes) -> Msg:
    """
    Serializes a msg from binary.
    """
    unpacked = msgpack.unpackb(data, timestamp=3)
    if issubclass(msg_cls, FastIoTData):
        return msg_cls(**unpacked)

    return unpacked
