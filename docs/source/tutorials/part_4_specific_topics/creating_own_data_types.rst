.. _tut-own_data_types:
============================
Creating your own data types
============================

As FastIoT only provides some very basic data types (s. :mod:`fastiot.msg`) many projects will require their own data
models.

As a rule of thumb it is recommended to use the :class:`fastiot.msg.thing.Thing` for single sensor values. This allows
any module to work with the data and common adaptors to provide the data. This should work well when e.g. reading out a
PLC or any other sensor device.

If you have more complex data to handle it is usually a good starting point in the project to think about how to
structure your data. This is done using data models.
FastIoT relies on `Pydantic <https://pydantic-docs.helpmanual.io/>`_, so you may consult this for any details about data
models.

To add the FastIoT handling of subjects it is recommended (though not necessary) to inherit your class from one of the
inheritors of :class:`fastiot.core.data_models.FastIoTData`.

Three basic classes inherit from this class:
 -  :class:`fastiot.core.data_models.FastIoTPublish` for data to be simply published like :class:`fastiot.msg.thing.Thing`.
    This will add the method :meth:`fastiot.core.data_models.FastIoTPublish.get_subject` and allow for an easy
    publish/subscribe as described in :ref:`publish-subscribe`.
 - :class:`fastiot.core.data_models.FastIoTRequest` to request data from other services. To define your datatype for the
   response please set the property :attr:`fastiot.core.data_models.FastIoTRequest._reply_cls` accordingly. To get the
   subject for the datatype please use :meth:`fastiot.core.data_models.FastIoTRequest.get_reply_subject`.
 - :class:`fastiot.core.data_models.FastIoTResponse` is the expected reply datatype for any request. This class does
   explicitly not provide any form of ``get_subject()`` as there are no subjects to subscribe to for an answer.


A very basic data model for publishing data could thus look like the following:

.. code:: python

  from typing import Optional, Union

  from fastiot.core.data_models import FastIoTPublish


  class MyDataModel(FastIoTPublish):
    my_id: str
    """ A required string """

    my_value: Union[float, int]
    """ An required float or integer """

    optional_value: Optional[str] = ""
    """ An optional value defaulting to an empty string """

