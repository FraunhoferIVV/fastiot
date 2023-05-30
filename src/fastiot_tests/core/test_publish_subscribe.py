import asyncio
import unittest
from datetime import datetime

from fastiot.core.broker_connection import NatsBrokerConnection
from fastiot.core.data_models import ReplySubject
from fastiot.core.service import FastIoTService
from fastiot.core.service_annotations import reply
from fastiot.msg.thing import Thing
from fastiot.testlib import populate_test_env

THING = Thing(machine='SomeMachine', name="RequestSensor", value=42, timestamp=datetime.now(), measurement_id="1")


class FastIoTTestService(FastIoTService):
    @reply(ReplySubject(name="ping", msg_cls=Thing, reply_cls=Thing))
    async def ping(self, msg: Thing) -> Thing:
        """ Short demo on receiving a thing value and sending back the duplication of its value """
        return msg

    @reply(ReplySubject(name="ping_with_subject", msg_cls=Thing, reply_cls=Thing))
    async def ping_with_subject(self, subject_name: str, msg: Thing) -> Thing:
        assert subject_name is not None
        return msg


class TestPublishSubscribe(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        populate_test_env()
        self.broker_connection = await NatsBrokerConnection.connect()
        service = FastIoTTestService(broker_connection=self.broker_connection)
        self.service_task = asyncio.create_task(service.run())

    async def asyncTearDown(self):
        self.service_task.cancel()
        await self.broker_connection.close()

    async def test_publish_subscribe(self):
        subject = Thing.get_subject(name='test_msg')

        async def cb(subject, msg):
            self.assertEqual(THING, msg)
            self.assertTrue('test_msg' in subject)

        subscription = await self.broker_connection.subscribe(subject=subject, cb=cb)
        await self.broker_connection.publish(subject, THING)
        await subscription.unsubscribe()

    async def test_request(self):
        request = THING
        subject = ReplySubject(name="ping", msg_cls=Thing, reply_cls=Thing)
        response = await self.broker_connection.request(subject=subject, msg=request)
        self.assertEqual(response, request)

    async def test_request_with_subject_name(self):
        request = THING
        subject = ReplySubject(name="ping_with_subject", msg_cls=Thing, reply_cls=Thing)
        response = await self.broker_connection.request(subject=subject, msg=request)
        self.assertEqual(response, request)


class TestPublishSubscribeException(unittest.IsolatedAsyncioTestCase):

    async def test_raise_exception_in_subscription(self):
        async def cb(*_):
            raise ValueError()

        populate_test_env()

        err = None
        event = asyncio.Event()

        async def error_cb(exception):
            nonlocal err
            err = exception
            event.set()

        subject = Thing.get_subject('something')
        broker_connection = await NatsBrokerConnection.connect(subscription_error_cb=error_cb)
        subscription = await broker_connection.subscribe(subject=subject, cb=cb)
        try:
            await broker_connection.publish(subject, THING)
            await asyncio.wait_for(event.wait(), 10)
            self.assertIsInstance(err, ValueError)
        finally:
            await subscription.unsubscribe()
            await broker_connection.close()


if __name__ == '__main__':
    unittest.main()
