from typing import List

from fastiot.core.data_models import FastIoTRequest, FastIoTResponse


class Response(FastIoTResponse):

    resp_value: float  # A float usually containing the average of requested numbers

class Request(FastIoTRequest):
    _reply_cls = Response
    req_value: List[int]  # A list of values
