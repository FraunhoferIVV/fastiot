import asyncio
from datetime import datetime

from fastiot import logging
from fastiot.core import FastIoTService, loop, subscribe, ReplySubject
from fastiot.msg.thing import Thing


class ExampleConsumerService(FastIoTService):

    @subscribe(subject=Thing.get_subject('*'))
    async def consume(self, topic: str, msg: Thing):
        logging.info("%s: %s", topic, str(msg))

    @loop
    async def request(self):
        request = Thing(machine='SomeMachine', name="RequestSensor", value=42, timestamp=datetime.now())
        subject = ReplySubject(name="reply_test", msg_cls=Thing, reply_cls=Thing)
        reply: Thing = await self.broker_connection.request(subject=subject, msg=request, timeout=10)
        logging.info("Got reply %s", str(reply))
        return asyncio.sleep(30)


if __name__ == '__main__':
    ExampleConsumerService.main()
