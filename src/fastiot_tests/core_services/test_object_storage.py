import asyncio
import unittest
from datetime import datetime, timedelta
from typing import List, Type, Union

from pydantic import BaseModel

from fastiot.core.broker_connection import NatsBrokerConnection
from fastiot.core.data_models import FastIoTData, ReplySubject, FastIoTPublish
from fastiot.core.subject_helper import sanitize_subject_name
from fastiot.db.mongodb_helper_fn import get_mongodb_client_from_env
from fastiot.env import env_mongodb
from fastiot.helpers.object_helper import parse_object, parse_object_list
from fastiot.msg.hist import HistObjectReq, HistObjectResp
from fastiot.msg.thing import Thing
from fastiot_core_services.object_storage.object_storage_helper_fn import to_mongo_data
from fastiot_core_services.object_storage.object_storage_service import ObjectStorageService
from fastiot_tests.generated import set_test_environment

THING = Thing(machine='SomeMachine', name="RequestSensor", value=42, timestamp=datetime.now(), measurement_id="1")


class TestValue(FastIoTPublish):
    real: float
    img: float


class TestCustomMsg(FastIoTPublish):
    x: TestValue
    y: TestValue


class TestCustomMsgList(FastIoTPublish):
    values: List[TestCustomMsg]


def convert_message_to_mongo_data(msg: Type[Union[Type[FastIoTData], BaseModel, dict]],
                                  subject: str, timestamp: datetime):
    mongo_data = to_mongo_data(timestamp=timestamp, subject_name=subject, msg=msg)
    return mongo_data


class TestObjectStorage(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        set_test_environment()
        self._db_client = get_mongodb_client_from_env()
        self._database = self._db_client.get_database(env_mongodb.name)
        self._db_col = self._database.get_collection('object_storage')
        self._db_col.delete_many({})
        self.broker_connection = await NatsBrokerConnection.connect()


    async def _start_service(self):
        service = ObjectStorageService(broker_connection=self.broker_connection)
        self.service_task = asyncio.create_task(service.run())
        await asyncio.sleep(0.005)

    async def asyncTearDown(self):
        self.service_task.cancel()

    async def test_thing_storage(self):
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
        hist_req_msg = HistObjectReq(dt_start=datetime(year=2022, month=10, day=9, second=0),
                                     dt_end=datetime(year=2022, month=10, day=9, second=10),
                                     limit=10, subject_name='v1.thing.sensor_0',
                                     query_dict={'machine': 'test_machine'})
        subject = hist_req_msg.get_reply_subject()

        await self._start_service()
        reply: HistObjectResp = await self.broker_connection.request(subject=subject, msg=hist_req_msg, timeout=10)
        values = [parse_object(v, Thing) for v in reply.values]
        self.assertEqual(expected_thing_list[0], values[0])

    async def test_request_response_object(self):
        await self._start_service()

        expected_object_list = []
        dt_start = datetime.utcnow()
        dt_end = datetime.utcnow() + timedelta(minutes=5)
        for _ in range(5):
            object_msg = TestCustomMsgList(
                values=[TestCustomMsg(x=TestValue(real=1, img=2),
                                      y=TestValue(real=1, img=2))])
            expected_object_list.append(object_msg)
            test_object_msg_mongo_dict = convert_message_to_mongo_data(
                msg=object_msg.dict(),
                subject=object_msg.get_subject().name,
                timestamp=datetime.utcnow())
            self._db_col.insert_one(test_object_msg_mongo_dict)

        hist_req_msg = HistObjectReq(dt_start=dt_start, dt_end=dt_end, limit=10,
                                     subject_name=sanitize_subject_name('test_custom_msg_list'))
        subject = hist_req_msg.get_reply_subject()

        reply: HistObjectResp = await self.broker_connection.request(subject=subject, msg=hist_req_msg, timeout=10)
        values = parse_object_list(reply.values, TestCustomMsgList)
        self.assertListEqual(expected_object_list, values)

    async def test_request_response_object_req_default(self):
        await self._start_service()

        expected_object_list = []
        dt_start = datetime.utcnow()
        dt_end = datetime.utcnow() + timedelta(minutes=5)
        for _ in range(5):
            object_msg = TestCustomMsgList(
                values=[TestCustomMsg(x=TestValue(real=1, img=2),
                                      y=TestValue(real=1, img=2))])
            expected_object_list.append(object_msg)
            test_object_msg_mongo_dict = convert_message_to_mongo_data(
                msg=object_msg.dict(),
                subject=object_msg.get_subject().name,
                timestamp=datetime.utcnow())
            self._db_col.insert_one(test_object_msg_mongo_dict)

        hist_req_msg = HistObjectReq()
        subject = hist_req_msg.get_reply_subject()

        reply: HistObjectResp = await self.broker_connection.request(subject=subject, msg=hist_req_msg, timeout=10)
        values = parse_object_list(reply.values[:-1], TestCustomMsgList)
        self.assertListEqual(expected_object_list, values)


if __name__ == '__main__':
    unittest.main()
