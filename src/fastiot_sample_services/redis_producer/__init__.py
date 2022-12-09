"""
=====================
Example Redis Producer
=====================

Redis Producer gives an example on how to interact with :class:`fastiot.db.redis_helper.RedisHelper`. He saves :class:`fastiot.msg.thing.Thing` objects via the
:class:`fastiot.db.redis_helper.RedisHelper` and publishes the Message under :class:`fastiot.msg.redis.RedisMsg`.
He also listens to messages published under Redis.>. and gets the corresponding Data from :class:`fastiot.db.redis_helper.RedisHelper`.
"""
