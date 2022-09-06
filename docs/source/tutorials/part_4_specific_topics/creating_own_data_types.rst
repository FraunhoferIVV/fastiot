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

To add the FastIoT handling of subjects it is recommended (though not necessary) to inherit your class from
:class:`fastiot.core.data_models.FastIoTData`. This will add the method
:meth:`fastiot.core.data_models.FastIoTData.get_subject` and allow for an easy publish/subscribe as described in
:ref:`publish-subscribe`.

A very basic data model could thus look like the following:

.. code:: python

  from typing import Optional, Union

  from fastiot.core.data_models import FastIoTData


  class MyDataModel(FastIoTData):
    my_id: str
    """ A required string """

    my_value: Union[float, int]
    """ An required float or integer """

    optional_value: Optional[str] = ""
    """ An optional value defaulting to an empty string """

