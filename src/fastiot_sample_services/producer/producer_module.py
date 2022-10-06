import asyncio
import random
from datetime import datetime

from fastiot import logging
from fastiot.core import FastIoTService, loop, reply, ReplySubject
from fastiot.msg.thing import Thing


class ExampleProducerService(FastIoTService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._logger = logging('producer')

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
        self._logger.info("Published %d on sensor %s", value, subject.name)
        return asyncio.sleep(2)

    @reply(ReplySubject(name="reply_test",
                        msg_cls=Thing,
                        reply_cls=Thing))
    async def respond(self, topic: str, msg: Thing) -> Thing:
        """ Short demo on receiving a thing value and sending back the duplication of its value """
        self._logger.info("Received request on topic %s with message %s.", topic, str(msg))
        new_thing_msg = msg
        new_thing_msg.value = 2 * msg.value
        return new_thing_msg


if __name__ == '__main__':
    ExampleProducerService.main()
