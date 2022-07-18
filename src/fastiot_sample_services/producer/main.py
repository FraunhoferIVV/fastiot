import asyncio
import logging
import random
from datetime import datetime

from fastiot.core.app import FastIoTService
from fastiot.core.app_annotations import loop
from fastiot.msg.thing import Thing


class MyService(FastIoTService):

    @loop
    async def produce(self):
        sensor_name = f'my_sensor_{random.randint(1,5)}'
        sensor = Thing.get_subject(sensor_name)
        value = random.randint(20, 30)
        await self.broker_connection.publish(
            subject=sensor,
            msg=Thing(
                name=sensor_name,
                machine= 'FastIoT_Example_Machine',
                value=value,
                timestamp=datetime.utcnow()
            )
        )
        logging.info("Published %d on sensor %s", value, sensor.name)
        return asyncio.sleep(2)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    MyService.main()
