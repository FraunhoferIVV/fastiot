from datetime import datetime
from typing import Any

from pydantic.main import BaseModel

from fastiot.core.subject import Subject


class Thing(BaseModel):
    value: Any
    timestamp: datetime

    @classmethod
    def get_subject(cls, name: str):
        return Subject(
            name=f"v1.thing.{name}",
            msg_cls=Thing
        )
