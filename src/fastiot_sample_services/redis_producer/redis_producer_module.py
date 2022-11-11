import asyncio
import logging
import random
from datetime import datetime

from fastiot.core import FastIoTService, loop, subscribe
from fastiot.helpers.redis_helper import RedisHelper
from fastiot.msg import Thing, RedisMsg
from fastiot.util.object_helper import parse_object


class ExampleRedisProducerService(FastIoTService):

    def __int__(self, **kwargs):
        super().__init__(**kwargs)
        helper = None

    async def _start(self):
        self.helper = RedisHelper(self.broker_connection)

    @loop
    async def produce(self):
        sensor_name = 'my_redis_sensor'
        value = random.randint(20, 30)
        subject = RedisMsg.get_subject(sensor_name)
        thing = Thing(
                name=sensor_name,
                machine='FastIoT_Example_Machine',
                value=value,
                unit="m",
                timestamp=datetime.utcnow())
        await self.helper.send_data(data=thing, subject=subject)
        return asyncio.sleep(2)

    @subscribe(subject=RedisMsg.get_subject("my_redis_sensor"))
    async def consume(self, msg: RedisMsg):
        thing: Thing = parse_object(await self.helper.get_data(msg.id), Thing)
        logging.info("%s: %s", msg.get_subject().name, str(thing))


if __name__ == '__main__':
    ExampleRedisProducerService.main()
