import asyncio
import logging
from datetime import datetime

from fastiot.core.service import FastIoTService
from fastiot.core.service_annotations import subscribe, loop
from fastiot.core.data_models import Subject
from fastiot.msg.thing import Thing


class MyService(FastIoTService):

    @subscribe(subject=Thing.get_subject('*'))
    async def consume(self, topic: str, msg: Thing):
        logging.info("%s: %s", topic, str(msg))

    @loop
    async def request(self):
        request = Thing(machine='SomeMachine', name="RequestSensor", value=42, timestamp=datetime.now())
        subject = Subject(name="reply_test", msg_cls=Thing, reply_cls=Thing)
        reply: Thing = await self.broker_connection.request(subject=subject, msg=request, timeout=10)
        logging.info("Got reply %s", str(reply))
        return asyncio.sleep(30)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    MyService.main()
