.. _publish-subscribe:

#####################################################
Publish, subscribe, request and reply in your service
#####################################################

The whole framework is based on messages, s. :ref:`architecture-overview` for details.

Subjects in nats and FastIoT
============================

The whole messing is based on Subjects you subscribe to or publish messages on. For details how this is handled within
nats.io please refer to their official documentation at https://docs.nats.io/nats-concepts/subjects

For FastIoT this results in two basic options:

1. You may use many (hierarchical) subjects if you send the same data type for multiple e.g. sensors. This is
   the case for the data type :class:`fastiot.msg.thing.Thing`, where many services will send their sensor data
   to many other services reading them. This allows to subscribe to a single subject (e.g. sensor) as well as to many
   subjects using wildcards (s. nats.io documentation for using wildcards).
2. You may use on subject for one data type. Especially if you have custom data types with well defined sources and
   sinks this is an option.

FastIoT only brings very basic data types defined in :mod:`fastiot.msg` coming with it’s own subjects. If you want to
define custom data models for your projects please refer to :ref:`tut-custom_data_types`.

Subscribing to an existing subject
==================================

To subscribe to an subject you just have to add a method to your service and decorate it with an ``@subscribe``.
:meth:`fastiot.core.service_annotations.subscribe` needs to have a :class:`fastiot.core.data_models.Subject` passed. The
easiest way to get the subject for a datamodel like ``Thing`` is to use its method ``get_subject`` which will
automatically create a subject for the datamodel. See :meth:`fastiot.core.data_models.FastIoTData.get_subject` for more
details.

.. code:: python

  from fastiot.core import FastIoTService, Subject, subscribe
  from fastiot.msg.thing import Thing

  class MyService(FastIoTService):

      @subscribe(subject=Thing.get_subject('*'))
      async def consume(self, topic: str, msg: Thing):
        """ Do something with the msg here! """

In this case a wildcard was used to receive all messages on the subject ``Thing.*``. This will work e.g. with
``Thing.sensor_1`` but not with ``Thing.machine.other_sensor``. To also subscribe everything below ``Thing`` you can use
the wildcard ``>`` like in ``Thing.>``. This will subscribe everything below ``Thing``, so ``machine`` but also
``other_machine``.

To subscribe to a non-hierarchical subject you can leave out the argument ``'*'``. This will then subscribe ``Thing``.

A working example can be found in the consumer example service: :class:`fastiot_sample_services.consumer.consumer_module.ExampleConsumerService`

Defining own subjects
---------------------

Instead of relying on the subject defined by data model you can also create you own subject:

.. code:: python

  @subscribe(subject=Subject(name='my_subject',
                             msg_cls=MyDataModel))

The message received will then be parsed into your ``MyDataModel``. You can also specify ``dict`` as a ``msg_class`` to
receive the message as plain dictionary. We strongly recommend to use Pydantic data models and not work with
dictionaries.

Publishing data
===============

Publishing data works on the same principle as receiving with a subscription regarding topics.
The following code will initiate a forever running loop and publish a message with the value 42 on the topic
``Thing.my_sensor`` with the current time. If you are not familiar with async please pay extra attention not to forget
the ``await`` before .

For a fully working example you may also consult :class:`fastiot_sample_services.producer.producer_module.ExampleProducerService`

.. code:: python

  import asyncio
  from datetime import datetime

  from fastiot.core import FastIoTService, Subject, loop
  from fastiot.core.core_uuid import get_uuid
  from fastiot.msg.thing import Thing


  class MyProducer(FastIoTService):

      @loop
      async def send_something(self):
          sensor_name = 'my_sensor'
          subject = Thing.get_subject(sensor_name)
          await self.broker_connection.publish(
              subject=subject,
              msg=Thing(
                  name=sensor_name,
                  machine='MyMachine', measurement_id=get_uuid(),
                  value=42, timestamp=datetime.utcnow()
              )
          )
          return asyncio.sleep(2)

If you want to send larger Files you can use
:class:`fastiot.helpers.redis_helper.RedisHelper`
.
As an example for an implementation of
:class:`fastiot.helpers.redis_helper.RedisHelper`
you can use
:class:`fastiot_sample_services.redis_producer.redis_producer_module.ExampleRedisProducerService`


Request and Reply
=================

Sometimes you may not kind of "shout" the data over the broker (publish) but make sure it arrives and you get a certain
response.

Therefore your responder needs to return a message at the end:

.. code:: python

  @reply(ReplySubject(name="reply",
                      msg_cls=Thing,
                      reply_cls=Thing))
  async def pong(self, topic: str, msg: Thing) -> Thing:
    return msg

This code will simply receive a ``Thing`` and return the same ``Thing`` as response.

The request for this looks similiar to a typical publish. We define an request message (here a ``ping_msg``), define a
subject (``reply``) and send an request.

.. code:: python

    async def request(self):
        ping_msg = Thing(machine='SomeMachine', name="RequestSensor", value=42, timestamp=datetime.now())
        subject = ReplySubject(name="reply", msg_cls=Thing, reply_cls=Thing)
        pong_msg: Thing = await self.broker_connection.request(subject=subject, msg=request, timeout=10)

All methods like ``request`` and ``reply`` can be imported from ``fastiot.core``.
