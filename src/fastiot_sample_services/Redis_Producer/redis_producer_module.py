import asyncio
import logging
import random
from datetime import datetime

from ormsgpack import ormsgpack

from fastiot.core import FastIoTService, loop, subscribe

from fastiot.helpers.redis_helper import RedisHelper
from fastiot.msg.thing import Thing, Redis


class ExampleRedisProducerService(FastIoTService):

    def __int__(self, **kwargs):
        super().__init__(**kwargs)
        helper = None

    async def _start(self):
        self.helper = RedisHelper(self.broker_connection)

    @loop
    async def produce(self):
        sensor_name = f'my_sensor_{random.randint(1, 5)}'
        value = random.randint(20, 30)
        subject = Redis.get_subject(sensor_name)
        thing = Thing(
                name=sensor_name,
                machine='FastIoT_Example_Machine',
                value=value,
                unit="m",
                timestamp=datetime.utcnow())
        await self.helper.send_data(data=thing, subject=subject)
        return asyncio.sleep(2)

    @subscribe(subject=Redis.get_subject(">"))
    async def consume(self, msg: Redis):
        helper = RedisHelper(self.broker_connection)
        thing = await helper.get_data(msg.id)
        logging.info("%s: %s", msg.get_subject().name, str(thing))

if __name__ == '__main__':
    ExampleRedisProducerService.main()
