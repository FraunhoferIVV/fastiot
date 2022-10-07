""" Messages handling queries to databases with historic data (time series or object storage) """
from datetime import datetime
from typing import List, Optional, Union

from pydantic.main import BaseModel

from fastiot.core.data_models import Subject, FastIoTResponse, FastIoTRequest
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


class HistObjectResp(FastIoTResponse):
    """
    This Class is used to answer the request for historical data.
    """
    error_code: int = 0
    """ error number """
    error_msg: str = ""
    """ if an error occurred you can get a detailed description """
    values: List[dict]
    """ the results of the request """


class HistObjectReq(FastIoTRequest):
    """
    This class is used for requesting historical data.

    After instancing HistObjectReq, a subject for requesting historical data must also be instanced, with the
    subject_name 'reply_object'.

    .. code:: python

      subject = HistObjectReq.get_reply_subject()
      ReplySubject(name='reply_object', msg_cls=HistObjectReq, reply_cls=HistObjectResp)

    """
    _reply_cls = HistObjectResp

    dt_start: Optional[datetime]
    """ is used to limit the time range. """
    dt_end: Optional[datetime]
    """ is used to limit the time range. """
    limit: Optional[int] = 100
    """ will limit the number of results. """
    subject_name: Optional[str]
    """ will search only the objects, which are saved under this subject_name.
     **CAUTION!** This is not the request-reply subject name. """
    machine: Optional[str]
    """ is used to return only the value of the given machine """
    sensor: Optional[str]
    """ is used to return only the value of the given sensor """
    raw_query: Optional[Union[dict, str]]
    """
    is an optional variable, you can also add your own query_dict, besides the default setting, which
    consists only `_subject` and `_timestamp`. Your default will be extended by query_dict, after ObjectStorage Service
    receives it.
    The handling of argument is subject to each service and may be handled different e.g. if using an InfluxDB time
    series storage or a MongoDB based object storage.

    .. code:: python

      query_dict = {'test_index': 'test'}
      HistObjectReq(dt_start=dt_start, dt_end=dt_end,
                    limit=10, subject_name=sanitize_subject('my_data_type'), raw_query=query_dict)

    """
