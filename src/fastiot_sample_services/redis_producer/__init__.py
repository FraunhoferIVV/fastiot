"""
======================
Example Redis Producer
======================

Redis Producer gives an example on how to interact with :class:`fastiot.db.redis_helper.RedisHelper`.

It  saves :class:`fastiot.msg.thing.Thing` objects via the :class:`fastiot.db.redis_helper.RedisHelper` and publishes
the message under :class:`fastiot.msg.redis.RedisMsg`.
It also listens to messages published under Redis.>. and gets the corresponding Data from
:class:`fastiot.db.redis_helper.RedisHelper`.

.. seealso::
   :class:`fastiot.db.redis_helper.RedisHelper`
      How to easily interact using the integrated RedisHelper.
   :class:`fastiot.cli.common.infrastructure_services.RedisService`
      The infrastructure service definition for the Redis Server.
   :mod:`fastiot_sample_services.redis_producer`
      Example service for sending and receiving data over a Redis Server.
"""
