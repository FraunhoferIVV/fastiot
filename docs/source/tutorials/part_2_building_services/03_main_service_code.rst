=============
Service Logic
=============

As the entry level (s. :ref:`tut-Service_Entry_Point`) usually does not contain the service logic. This is done a file
like ``my_service_module.py``.  This file contains the actual logic. This file should also be created automatically if
you use the FastIoT CLI for project and service creation.

A basic service is always inherited from :class:`fastiot.core.service.FastIoTService`. For more details thus please
consult the corresponding API documentation.

.. code:: python

  import asyncio

  from fastiot.core import FastIoTService, loop

  class ExampleProducerService(FastIoTService):
      def __init__(self, **kwargs):
        """
        An own __init__ is usually not required. If you use this please don’t forget to run the __init__ of the
        super class!
        """
        super().__init__(**kwargs)

      async def _start(self):
        """
        If you need to run any async starting operations you may implement this ``_start`` method,
        which is always async
        """

      @loop
      def some_looping_method():
        """
        Decorate a method with ``@loop`` to have it run forever till the service exits.
        """
        return asyncio.sleep(1)


Import concepts specific to the FastIoT Framework are the the implementation of
:meth:`fastiot.core.service.FastIoTService._start` to start any async tasks on your own and using loops with the
decorator :func:`fastiot.core.service_annotations.loop`.

For subscribing to subjects and publishing messages please refer to the next tutorial: :ref:`publish-subscribe`.