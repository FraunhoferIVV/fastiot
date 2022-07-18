from datetime import datetime
from typing import List

from pydantic.main import BaseModel

from fastiot.core.subject import Subject
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


class HistResp(BaseModel):
    name: str
    values: List[Thing]


class HistReq(BaseModel):
    name: str
    dt_start: datetime
    dt_end: datetime = None
    max_values: int = None

    @classmethod
    def get_hist_subject(cls, name: str):
        return Subject(
            name=f"v1.hist.{name}",
            msg_cls=HistReq,
            reply_cls=HistResp
        )
