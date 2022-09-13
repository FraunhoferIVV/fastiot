import asyncio
import unittest
from datetime import datetime
from typing import List

from pydantic import BaseModel
from fastiot.core.broker_connection import NatsBrokerConnection

from fastiot.core.data_models import FastIoTData, ReplySubject, Subject
from fastiot.db.mongodb_helper_fn import get_mongodb_client_from_env
from fastiot.env import env_mongodb
from fastiot.msg.hist import HistThingReq, HistThingResp
from fastiot.msg.thing import Thing
from fastiot_core_services.object_storage.object_storage_fn import convert_message_to_mongo_data
from fastiot_core_services.object_storage.object_storage_service import ObjectStorageService
from fastiot_tests.core.test_publish_subscribe import FastIoTTestService
from fastiot_tests.generated import set_test_environment

THING = Thing(machine='SomeMachine', name="RequestSensor", value=42, timestamp=datetime.now(), measurement_id="1")


class TestValue(FastIoTData):
    real: float
    img: float


class TestCustumeMsg(FastIoTData):
    x: TestValue
    y: TestValue


class TestCustumeMsgList(FastIoTData):
    name: str
    timestamp: datetime
    subject: str
    measurement_id: str
    values: List[TestCustumeMsg]

    def get_dict(self):
        return {"name": self.name, "timestamp": self.timestamp, "subject": TestCustumeMsgList.get_subject().name,
                "measurement_id": self.measurement_id, "values": self.dict()["values"]}


class TestPublishSubscribe(unittest.IsolatedAsyncioTestCase):

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

    def test_thing_dict_to_mongo(self):
        thing_msg = Thing(machine='test_machine', name='test_thing', measurement_id='123456',
                          value=1, timestamp=datetime(year=2022, month=10, day=10, second=1))
        test_thing_msg_mongo_dict = convert_message_to_mongo_data(thing_msg.dict())
        self.assertEqual('123456', test_thing_msg_mongo_dict['Object']['measurement_id'])
        self._db_col.insert_one(test_thing_msg_mongo_dict)

    async def test_thing_storage(self):
        thing_msg = Thing(machine='test_machine', name='test_thing', measurement_id='123456',
                          value=1, timestamp=datetime(year=2022, month=10, day=10, second=1))

        await self._start_service()
        await self.broker_connection.publish(Thing.get_subject(), thing_msg)
        await asyncio.sleep(0.02)

    def test_query_thing(self):
        self._db_col.delete_many({})
        for i in range(5):
            thing_msg = Thing(machine='test_machine', name='test_thing', measurement_id='123456',
                              value=1, timestamp=datetime(year=2022, month=10, day=9, second=i))
            test_thing_msg_mongo_dict = convert_message_to_mongo_data(thing_msg.dict())
            self._db_col.insert_one(test_thing_msg_mongo_dict)

        hist_req_msg = HistThingReq(machine='test_machine', name='test_thing',
                                    dt_start=datetime(year=2022, month=10, day=9, second=0),
                                    dt_end=datetime(year=2022, month=10, day=9, second=10))
        query_dict = {'timestamp': {'$gte': hist_req_msg.dt_start, '$lte': hist_req_msg.dt_end},
                      'Object.machine': 'test_machine',
                      'Object.name': 'test_thing'}
        query_result = list(self._db_col.find(query_dict))
        self.assertEqual(len(query_result), 5)

    async def test_reqeust_response_thing(self):
        self._db_col.delete_many({})
        expected_thing_list = []
        for i in range(5):
            thing_msg = Thing(machine='test_machine', name='test_thing', measurement_id='123456',
                              value=1, timestamp=datetime(year=2022, month=10, day=9, second=i))
            expected_thing_list.append(thing_msg)
            test_thing_msg_mongo_dict = convert_message_to_mongo_data(thing_msg.dict())
            self._db_col.insert_one(test_thing_msg_mongo_dict)
        hist_req_msg = HistThingReq(machine='test_machine', name='test_thing',
                                    dt_start=datetime(year=2022, month=10, day=9, second=0),
                                    dt_end=datetime(year=2022, month=10, day=9, second=10))
        subject = ReplySubject(name='reply_thing', msg_cls=HistThingReq, reply_cls=HistThingResp)

        await self._start_service()
        reply: HistThingResp = await self.broker_connection.request(subject=subject, msg=hist_req_msg, timeout=10)
        self.assertListEqual(expected_thing_list, reply.values)

    def test_basemodel_dict_to_mongo(self):
        test_custume_msg_l = TestCustumeMsgList(
            name='test_custume_m',
            timestamp=datetime(year=2022, month=10, day=10, second=1),
            subject=TestCustumeMsgList.get_subject().name,
            measurement_id='12345',
            values=[TestCustumeMsg(x=TestValue(real=1, img=2),
                                   y=TestValue(real=1, img=2)),
                    TestCustumeMsg(x=TestValue(real=3, img=4),
                                   y=TestValue(real=3, img=4)),
                    TestCustumeMsg(x=TestValue(real=5, img=6),
                                   y=TestValue(real=5, img=6))])

        test_custume_msg_mongo_dict = convert_message_to_mongo_data(test_custume_msg_l.get_dict())
        self.assertEqual('12345', test_custume_msg_mongo_dict['Object']['measurement_id'])
        self.assertEqual(test_custume_msg_mongo_dict['_subject'], TestCustumeMsgList.get_subject().name)
        self._db_col.insert_one(test_custume_msg_mongo_dict)

    async def test_basemodel_storage(self):
        test_custume_msg_l = TestCustumeMsgList(
            name='test_custume_m',
            timestamp=datetime(year=2022, month=10, day=10, second=1),
            subject=TestCustumeMsgList.get_subject().name,
            measurement_id='12345',
            values=[TestCustumeMsg(x=TestValue(real=1, img=2),
                                   y=TestValue(real=1, img=2)),
                    TestCustumeMsg(x=TestValue(real=3, img=4),
                                   y=TestValue(real=3, img=4)),
                    TestCustumeMsg(x=TestValue(real=5, img=6),
                                   y=TestValue(real=5, img=6))])

        await self._start_service()
        await self.broker_connection.publish(test_custume_msg_l.get_subject(), test_custume_msg_l)
        await asyncio.sleep(0.02)


if __name__ == '__main__':
    unittest.main()
