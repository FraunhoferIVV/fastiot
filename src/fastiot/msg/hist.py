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
    This class is used for requesting historical data.

    :param dt_start: are used to limit the time range.
    :param dt_end: are used to limit the time range.
    :param limit: will limit the number of results.
    :param subject_name: will search only the objects, which are saved under this subject_name, **CAUTION!** This is not the request-reply subject name.
    :param query_dict: is an optional variable, you can also add your own query_dict, besides the default setting, which consists only `_subject` and `_timestamp`. Your default will be extended by query_dict, after ObjectStorage Service receives it.

    .. code:: python

      query_dict = {'test_index': 'test'}
      >>> HistObjectReq(dt_start=dt_start, dt_end=dt_end, limit=10, subject_name=sanitize_subject('my_data_type'), query_dict=query_dict)


    After instancing HistObjectReq, a subject for requesting historical data must also be instanced, with the subject_name 'reply_object'.

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
