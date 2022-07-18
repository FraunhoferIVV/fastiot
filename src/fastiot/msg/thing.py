from datetime import datetime
from typing import Any

from fastiot.core.data_models import FastIoTData


class Thing(FastIoTData):
    """
    Default data model for sending Things (e.g. Sensors) values.

    This model expects a hierarchy, thus when subscribing always set the name to the sensor name you are looking for or
    to ``*`` to subscribe all sensors. See  :meth:`fastiot.core.data_models.FastIoTData.get_subject` for more details!.
    """

    machine: str
    """ Name of the machine. If you have many machines you may add the vendor to the machine name. """
    name: str
    """ Name of the thing or sensor. """
    value: Any
    """ Any data type suitable for Pydantic and serializable by ``ormsgpack`` may be used.
    Be aware, that the receiving site needs no be able to cope with whatever you send.
    
    We recommend to stick to int, float and string and create your own data models based on
    :class:`fastiot.core.subject.FastIoTData` if want to sent more advanced data.
    """
    timestamp: datetime
    """ Timestamp for the value.
        
    It is recommended to always use UTC times (Function ``datetime.utcnow()``).
    """
