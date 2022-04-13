import random
from typing import Type, Any

from pydantic import BaseModel, root_validator


class Subject(BaseModel):
    name: str
    msg_cls: Type[BaseModel]
    reply_cls: Type[BaseModel] = None
    stream_mode = False

    @root_validator
    def check_valid_fields(cls, values):
        if 'stream_mode' in values and values['stream_mode'] is True:
            if 'reply_cls' not in values or values['reply_cls'] is None:
                raise ValueError("Stream mode only with reply_cls allowed")

    def create_generic_reply_inbox(self) -> "Subject":
        if self.reply_cls is None:
            raise ValueError("Cannot create generic inbox: reply_cls must not be none")

        return Subject(
            name='_INBOX' + str(random.randint(0, 1000000000)),
            msg_cls=self.reply_cls
        )

    def get_reply_inbox(self, reply_to: str) -> "Subject":
        return Subject(
            name=reply_to,
            msg_cls=self.reply_cls
        )
