import asyncio
import random
from datetime import datetime

from fastiot import logging
from fastiot.core import FastIoTService, loop, reply, ReplySubject
from fastiot.core.broker_connection import NatsBrokerConnection
from fastiot.helpers.Redis_Helper import RedisHelper
from fastiot.msg.thing import Thing


class ExampleRedisProducerService(FastIoTService):

    broker = None

    async def _start(self):
        self.broker = await NatsBrokerConnection.connect()

    @loop
    async def produce(self):
        sensor_name = f'my_sensor_{random.randint(1, 5)}'
        data = f'{random.randint(20, 30)}'
        helper = RedisHelper(self.broker_connection)
        await helper.sendData(data=data, source=sensor_name)
        return asyncio.sleep(2)


if __name__ == '__main__':
    ExampleRedisProducerService.main()
