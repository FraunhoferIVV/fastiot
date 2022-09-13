from typing import Type, Union

from pydantic import BaseModel

from fastiot.core.core_uuid import get_uuid
from fastiot.core.data_models import FastIoTData
from fastiot.msg.thing import Thing


def convert_message_to_mongo_data(msg: Type[Union[FastIoTData, BaseModel, dict]]):
    _id = get_uuid()

    if 'subject' not in list(msg.keys()):
        thing = Thing.parse_obj(msg)
        _subject = thing.get_subject()
        _timestamp = thing.timestamp
        return {"_id": get_uuid(),
                "_subject": _subject.name,
                "timestamp": _timestamp,
                "Object": thing.dict()}

    _subject = msg['subject']
    _timestamp = msg['timestamp']

    return {"_id": get_uuid(),
            "_subject": _subject,
            "_timestamp": _timestamp,
            "Object": msg}
