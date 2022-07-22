from typing import List

from fastiot.core.data_models import FastIoTData


class Request(FastIoTData):
    req_value: List[int]  # A list of values


class Response(FastIoTData):
    resp_value: float  # A float usually containing the average of requested numbers
