import asyncio
import unittest
from datetime import datetime

from fastiot.core.broker_connection import NatsBrokerConnectionImpl
from fastiot.core.data_models import Subject
from fastiot.core.service import FastIoTService
from fastiot.core.service_annotations import reply
from fastiot.msg.thing import Thing
from fastiot_tests.generated import set_test_environment

THING = Thing(machine='SomeMachine', name="RequestSensor", value=42, timestamp=datetime.now())


class FastIoTTestService(FastIoTService):
    @reply(Subject(name="ping", msg_cls=Thing, reply_cls=Thing))
    async def ping(self, topic: str, msg: Thing) -> Thing:
        """ Short demo on receiving a thing value and sending back the duplication of its value """
        return msg


class TestPublishSubscribe(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        set_test_environment()
        self.broker_connection = await NatsBrokerConnectionImpl.connect()
        service = FastIoTTestService(broker_connection=self.broker_connection)
        self.service_task = asyncio.create_task(service.run())

    async def asyncTearDown(self):
        self.service_task.cancel()

    async def test_publish_subscribe(self):
        subject = Thing.get_subject(name='test_msg')

        async def cb(topic, msg):
            self.assertEqual(THING, msg)
            self.assertTrue('test_msg' in topic)

        subscription = await self.broker_connection.subscribe(subject=subject, cb=cb)
        await self.broker_connection.publish(subject, THING)
        await subscription.unsubscribe()

    async def test_request(self):
        request = THING
        subject = Subject(name="ping", msg_cls=Thing, reply_cls=Thing)
        response: Thing = await self.broker_connection.request(subject=subject, msg=request)
        self.assertEqual(response, request)


if __name__ == '__main__':
    unittest.main()
