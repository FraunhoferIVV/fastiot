import asyncio
import logging
import random
from datetime import datetime

from fastiot.core import FastIoTService, Subject, loop, reply
from fastiot.msg.thing import Thing


class MyService(FastIoTService):

    @loop
    async def produce(self):
        sensor_name = f'my_sensor_{random.randint(1, 5)}'
        value = random.randint(20, 30)
        subject = Thing.get_subject(sensor_name)
        await self.broker_connection.publish(
            subject=subject,
            msg=Thing(
                name=sensor_name,
                machine='FastIoT_Example_Machine',
                value=value,
                timestamp=datetime.utcnow()
            )
        )
        logging.info("Published %d on sensor %s" %(value, subject.name))
        return asyncio.sleep(2)

    @reply(Subject(name="reply_test",
                   msg_cls=Thing,
                   reply_cls=Thing))
    async def respond(self, topic: str, msg: Thing) -> Thing:
        """ Short demo on receiving a thing value and sending back the duplication of its value """
        logging.info("Received request on topic %s with message %s.", topic, str(msg))
        new_thing_msg = msg
        new_thing_msg.value = 2 * msg.value
        return new_thing_msg


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    MyService.main()

