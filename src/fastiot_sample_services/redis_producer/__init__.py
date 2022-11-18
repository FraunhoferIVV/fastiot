"""
=====================
Example Redis Producer
=====================

Redis Producer gives an example on how to interact with :class:`fastiot.helpers.redis_helper.RedisHelper`. He saves :class:`fastiot.msg.thing.Thing` objects via the
:class:`fastiot.helpers.redis_helper.RedisHelper` and publishes the Message under :class:`fastiot.msg.redis.RedisMsg`.
He also listens to messages published under Redis.>. and gets the corresponding Data from :class:`fastiot.helpers.redis_helper.RedisHelper`.
"""
