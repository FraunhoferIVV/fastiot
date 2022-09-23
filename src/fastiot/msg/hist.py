from datetime import datetime
from typing import List, Dict

from pydantic.main import BaseModel

from fastiot.core.data_models import Subject, FastIoTData, ReplySubject
from fastiot.msg.thing import Thing


class HistBeat(BaseModel):
    dt_start: datetime
    name: str

    @classmethod
    def get_stream_subject(cls, name: str):
        return Subject(
            name=f"v1.hist.{name}",
            msg_cls=HistBeat,
            reply_cls=Thing,
            stream_mode=True
        )


class HistObjectResp(FastIoTData):
    values: List[Dict]


class HistObjectReq(FastIoTData):
    """
    This class is the request class for historical data.
    **dt_start** and **dt_end** are used to limit the timestamp,
    **limit** will limit the number of results,
    **subject_name** will search only the objects, which are saved under this subject_name, this is not the reply subject name,

    .. code:: python

      HistObjectReq(dt_start=dt_start, dt_end=dt_end, limit=10, subject_name=sanitize_subject('my_data_type'))

    **query_dict** is a optional variable, you can also add your own query_dict, besides the default dict.
    Your query_dict will extend it:

    .. code:: python

      {'_subject': xxx, '_timestamp': xxx}

    After instancing HistObjectReq, a subject for requesting historical data must also be instanced.

    .. code:: python

      subject = HistObjectReq.get_subject()
      >>> ReplySubject(name='reply_object', msg_cls=HistObjectReq, reply_cls=HistObjectResp)

    """
    dt_start: datetime
    dt_end: datetime
    limit: int
    subject_name: str
    query_dict: dict = None

    @classmethod
    def get_subject(cls) -> "ReplySubject":
        return ReplySubject(name='reply_object',
                            msg_cls=HistObjectReq,
                            reply_cls=HistObjectResp)
