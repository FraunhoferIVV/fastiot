import asyncio
import unittest
from datetime import datetime, timedelta
from typing import List, Type, Union

from pydantic import BaseModel
from fastiot.core.broker_connection import NatsBrokerConnection

from fastiot.core.data_models import FastIoTData, ReplySubject, Subject
from fastiot.db.mongodb_helper_fn import get_mongodb_client_from_env
from fastiot.env import env_mongodb
from fastiot.msg.hist import HistObjectReq, HistObjectResp
from fastiot.msg.thing import Thing
from fastiot_core_services.object_storage.object_storage_service import ObjectStorageService
from fastiot_tests.core.test_publish_subscribe import FastIoTTestService
from fastiot_tests.generated import set_test_environment

THING = Thing(machine='SomeMachine', name="RequestSensor", value=42, timestamp=datetime.now(), measurement_id="1")


class TestValue(FastIoTData):
    real: float
    img: float


class TestCustomMsg(FastIoTData):
    x: TestValue
    y: TestValue


class TestCustomMsgList(FastIoTData):
    values: List[TestCustomMsg]


def convert_message_to_mongo_data(msg: Type[Union[FastIoTData, BaseModel, dict]], subject: str, timestamp: datetime):
    _subject = subject
    _timestamp = timestamp
    return {"_subject": _subject,
            "_timestamp": _timestamp,
            "Object": msg}


class TestObjectStorage(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        set_test_environment()
        self._db_client = get_mongodb_client_from_env()
        self._database = self._db_client.get_database(env_mongodb.name)
        self._db_col = self._database.get_collection('object_storage')
        self.broker_connection = await NatsBrokerConnection.connect()
        service = FastIoTTestService(broker_connection=self.broker_connection)
        self.service_task = asyncio.create_task(service.run())

    async def _start_service(self):
        service = ObjectStorageService(broker_connection=self.broker_connection)
        self.service_task = asyncio.create_task(service.run())
        await asyncio.sleep(0.005)

    async def asyncTearDown(self):
        self.service_task.cancel()

    async def test_thing_storage(self):
        self._db_col.delete_many({})
        await self._start_service()
        for i in range(5):
            thing_msg = Thing(machine='test_machine', name=f'sensor_{i}', measurement_id='123456',
                              value=1, timestamp=datetime(year=2022, month=10, day=10, second=i))

            await self.broker_connection.publish(Thing.get_subject(thing_msg.name), thing_msg)
        await asyncio.sleep(0.02)
        results = self._db_col.find({})
        values = [value for value in results]
        self.assertEqual(values[0]['_subject'], 'v1.thing.sensor_0')

    async def test_object_storage(self):
        self._db_col.delete_many({})
        test_custom_msg_l = TestCustomMsgList(
            values=[TestCustomMsg(x=TestValue(real=1, img=2),
                                  y=TestValue(real=1, img=2))])

        await self._start_service()
        await self.broker_connection.publish(test_custom_msg_l.get_subject(), test_custom_msg_l)
        await asyncio.sleep(0.02)
        results = self._db_col.find({})
        values = [value for value in results]
        self.assertEqual(len(values[0]), 4)

    async def test_reqeust_response_thing(self):
        self._db_col.delete_many({})
        expected_thing_list = []
        for i in range(5):
            thing_msg = Thing(machine='test_machine', name='test_thing', measurement_id='123456',
                              value=1, timestamp=datetime(year=2022, month=10, day=9, second=i))
            expected_thing_list.append(thing_msg)
            test_thing_msg_mongo_dict = convert_message_to_mongo_data(
                msg=thing_msg.dict(),
                subject=Thing.get_subject(f'sensor_{i}').name,
                timestamp=datetime(year=2022, month=10, day=9, second=i))
            self._db_col.insert_one(test_thing_msg_mongo_dict)
        hist_req_msg = HistObjectReq(machine='test_machine', name='test_thing',
                                     dt_start=datetime(year=2022, month=10, day=9, second=0),
                                     dt_end=datetime(year=2022, month=10, day=9, second=10))
        subject = ReplySubject(name='reply_object', msg_cls=HistObjectReq, reply_cls=HistObjectResp)

        await self._start_service()
        reply: HistObjectResp = await self.broker_connection.request(subject=subject, msg=hist_req_msg, timeout=10)
        values = [Thing.parse_obj(v) for v in reply.values]
        self.assertListEqual(expected_thing_list, values)

    async def test_request_response_object(self):
        self._db_col.delete_many({})
        expected_object_list = []
        dt_start = datetime.utcnow()
        dt_end = datetime.utcnow() + timedelta(minutes=5)
        for i in range(5):
            object_msg = TestCustomMsgList(
                values=[TestCustomMsg(x=TestValue(real=1, img=2),
                                      y=TestValue(real=1, img=2))])
            expected_object_list.append(object_msg)
            test_object_msg_mongo_dict = convert_message_to_mongo_data(
                msg=object_msg.dict(),
                subject=object_msg.get_subject().name,
                timestamp=datetime.utcnow())
            self._db_col.insert_one(test_object_msg_mongo_dict)

        hist_req_msg = HistObjectReq(machine='test_machine', name='test_object',
                                     dt_start=dt_start,
                                     dt_end=dt_end)
        subject = ReplySubject(name='reply_object', msg_cls=HistObjectReq, reply_cls=HistObjectResp)

        await self._start_service()
        reply: HistObjectResp = await self.broker_connection.request(subject=subject, msg=hist_req_msg, timeout=10)
        values = [TestCustomMsgList.parse_obj(v) for v in reply.values]
        self.assertListEqual(expected_object_list, values)


if __name__ == '__main__':
    unittest.main()
