import random
import re
from typing import Type, Optional, Union

from pydantic import BaseModel, root_validator


class FastIoTData(BaseModel):
    """ Basemodel for all data types / data models to be transferred over the broker between the services.
    This is basically a Pydantic model with the additional handling of subjects. So any Pydantic model should work here,
    as long as it can be serialized using the library ``ormsgpack``.

    The subject is constructed from the model name, e.g. if your data model is called ``MySpecialModel`` a subject
    ``v1.my_special_subject`` will be created. If you want to have more control over the subject name you may overwrite
    the method :meth:`fastiot.core.data_models.FastIoTData.get_subject` in your data model or create a new model based
    on Pydantic’s :class:`pydantic.BaseModel`.
    """

    @classmethod
    def get_subject(cls, name: Optional[str] = "") -> "Subject":
        """
        This method returns the corresponding subject for the data model as :class:`fastiot.core.data_models.Subject`.

        :param name: The name of the subject. Please pay special attention to this parameter: The default is set to
                     ``""``. This works well for data models without hierarchies. In this case you will just subscribe
                     to ``v1.my_special_data_model``. If you use many sensors, like in the data model
                     :class:`fastiot.msg.ting.Thing` you have to provide a name. Then you can subscribe to
                     ``v1.thing.my_sensor``. If you want to subscribe to all sensors use ``*`` as name.
        """
        subject_name = f"v1.{re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()}"  # Convert CamelCase to snake_case
        if name:
            subject_name += "." + name
        return Subject(
            name=subject_name,
            msg_cls=cls
        )


class Subject(BaseModel):
    """ General model to handle subjects for subscriptions within the framework. """
    # pylint: disable=no-self-argument

    name: str
    """ Name of the subject, s. :meth:`fastiot.core.data_models.FastIoTData.get_subject` for details about subscription
    names."""
    msg_cls: Type[Union[FastIoTData, BaseModel, dict]]
    """ Datatype the message will provide. """
    reply_cls: Type[Union[FastIoTData, BaseModel, dict]] = None
    """ Set to a datatype, not the default ``None`` to expect a reply in this datatype. """
    stream_mode = False
    """ Enable streaming mode. """

    @root_validator
    def check_valid_fields(cls, values):
        if 'stream_mode' in values and values['stream_mode'] is True:
            if 'reply_cls' not in values or values['reply_cls'] is None:
                raise ValueError("Stream mode only with reply_cls allowed")
        return values

    def make_generic_reply_inbox(self) -> "Subject":
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
