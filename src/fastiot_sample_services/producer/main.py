import asyncio
import logging
import random
from datetime import timedelta, datetime

from fastiot.core.app import FastIoTService
from fastiot.core.app_annotations import loop
from fastiot.core.broker_connection import BrokerConnection, BrokerConnectionImpl
from fastiot.msg.thing import Thing


class MyService(FastIoTService):

    @loop
    async def produce(self):
        sensor = Thing.get_subject('my_sensor')
        await self.broker_connection.publish(
            subject=sensor,
            msg=Thing(
                value=random.randint(20, 30),
                timestamp=datetime.utcnow()
            )
        )
        return asyncio.sleep(2)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    MyService.main()
