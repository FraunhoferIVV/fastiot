from fastiot.core import FastIoTPublish


class RedisMsg(FastIoTPublish):
    id: str
    """ Id the data is stored under """
