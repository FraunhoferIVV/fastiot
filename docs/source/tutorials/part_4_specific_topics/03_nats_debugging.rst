Debugging message flow between services
=======================================

Debugging nats messages with telnet
-----------------------------------

If you are not sure if your data is handled by the nats broker correctly you can use telnet for debugging.

Run :command:`telnet localhost 4222` (or whatever your configuration looks like) in the terminal.

Subscribe to topics with ``SUB my.topic 10`` and you will see the messages passing by. Use a different number for each subscription.

Messages are msgpack encoded, so some values are easily human readable whereas some, like numbers, are encoded in non-printable characters (bitwise 0 for example for the number 0).

The topic is usually defined in the code like the following

.. code-block:: python

    class Thing(FastIoTData):
        name: str
        value: float

This block results in the subject name ``v1.thing``, optionally amended by a (sensor) name (details at
:meth:`fastiot.core.data_models.FastIoTData.get_subject`)

You may also use wildcards to subscribe on certain dot-seperated topics.
E.g. to subscribe to all subjects within machine you can use subscribe to ``v1.*`` wich will result in
``v1.thing`` and ``machine.stuff`` but not in ``machine.thing.mysensor``. Subscribe to ``v1.>```
to get all topics below ``v1``. For more details you may also consider the official nats.io documentation under
https://docs.nats.io/nats-concepts/subjects


A more sophisticated approach using a docker image
--------------------------------------------------

Using telnet you will not see the decoded values, e.g. a numeric 0 will be a ``0x00``. For this purpose a little module
is available.
For documentation please see the :mod:`fastiot_core_services.nats_logger`
