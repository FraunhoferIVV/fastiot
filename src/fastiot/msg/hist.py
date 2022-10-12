""" Messages handling queries to databases with historic data (time series or object storage) """
from datetime import datetime
from typing import List, Optional, Union

from pydantic.main import BaseModel

from fastiot.core.data_models import Subject, FastIoTResponse, FastIoTRequest
from fastiot.msg.thing import Thing


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
    This class is used for requesting historical data of your data type.

    You can instance a HistObjectReq object like following:

    .. code:: python

      query_dict = {'test_index': 'test'}
      hist_object_req_msg = HistObjectReq(dt_start=dt_start, dt_end=dt_end, limit=10, subject_name=sanitize_subject('my_data_type'), raw_query=query_dict)

    More details about sanitize_subject_name() see :func:`fastiot.core.subject_helper.sanitize_subject_name`
    This subject_name inside the HistObjectReq is the subject_name, that your data type has.
    Your data, which will be saved in mongodb, always contains this subject_name: 'v1.my_data_type'.

    After instancing HistObjectReq, a subject for requesting historical data must also be instanced, with the
    name 'my_data_type'.

    .. code:: python

      reply_subject = hist_object_req_msg.get_reply_subject('my_data_type')

    Then you will have a ReplySubject object like:

    >>> ReplySubject(name='v1.hist_object_req.my_data_type', msg_cls=HistObjectReq, reply_cls=HistObjectResp)

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

    """
