from datetime import datetime
from typing import Any

from fastiot.core.core_uuid import get_uuid
from fastiot.core.data_models import FastIoTPublish


MEASUREMENT_ID = get_uuid()


class Thing(FastIoTPublish):
    """
    Default data model for sending Things (e.g. Sensors) values.

    This model expects a hierarchy, thus when subscribing always set the name to the sensor name you are looking for or
    to ``*`` to subscribe all sensors. See  :meth:`fastiot.core.data_models.FastIoTData.get_subject` for more details!.
    """

    machine: str
    """ Name of the machine. If you have many machines you may add the vendor to the machine name. """
    name: str
    """ Name of the thing or sensor. """
    measurement_id: str = MEASUREMENT_ID
    """ Measurement id for this thing or sensor. The measurement id is intended to be unique across a measurement. If
    the data producer is restarted, it should change. This can be useful e.g. if a measurement is messed up and needs
    to be removed. Per default a UUID will be generated upon system start for this property.
    """
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
    unit: str = ""
    """ Optional add a unit, e.g. 's' to the measurement. """

class Address(FastIoTPublish):
    publisher: str
    """instance who published the Data"""

    client: str
    """client to querry database"""

    address: str
    """address where the data is stored"""