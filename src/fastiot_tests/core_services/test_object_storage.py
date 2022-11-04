import asyncio
import os
import unittest
from datetime import datetime, timedelta
from typing import List, Type, Union

from pydantic import BaseModel

from fastiot.core.broker_connection import NatsBrokerConnection
from fastiot.core.data_models import FastIoTData, FastIoTPublish
from fastiot.core.subject_helper import sanitize_pub_subject_name, filter_specific_sign
from fastiot.db.mongodb_helper_fn import get_mongodb_client_from_env
from fastiot.env import env_mongodb, FASTIOT_SERVICE_ID
from fastiot.msg.hist import HistObjectReq, HistObjectResp
from fastiot.msg.thing import Thing
from fastiot.testlib import populate_test_env
from fastiot.util.object_helper import parse_object, parse_object_list
from fastiot_core_services.object_storage.mongodb_handler import MongoDBHandler
from fastiot.msg.custom_db_data_type_conversion import to_mongo_data
from fastiot_core_services.object_storage.object_storage_service import ObjectStorageService

THING = Thing(machine='SomeMachine', name="RequestSensor", value=42, timestamp=datetime.now(), measurement_id="1")


class FIOTTestValue(FastIoTPublish):
    real: float
    img: float


class CustomTestMsg(FastIoTPublish):
    x: FIOTTestValue
    y: FIOTTestValue


class CustomTestMsgList(FastIoTPublish):
    values: List[CustomTestMsg]


def convert_message_to_mongo_data(msg: Type[Union[Type[FastIoTData], BaseModel, dict]],
                                  subject: str, timestamp: datetime):
    mongo_data = to_mongo_data(timestamp=timestamp, subject_name=subject, msg=msg)
    return mongo_data


class TestObjectStorage(unittest.IsolatedAsyncioTestCase):

    def get_mongo_col(self, service_id: str, collection_name: str):
        os.environ[FASTIOT_SERVICE_ID] = service_id
        self._db_client = MongoDBHandler()
        database = self._db_client.get_database(env_mongodb.name)
        self._db_col = database.get_collection(collection_name)

    async def asyncSetUp(self):
        populate_test_env()
        self._db_client = get_mongodb_client_from_env()
        self._database = self._db_client.get_database(env_mongodb.name)
        self._db_col = self._database.get_collection('object_storage')
        self._db_col.delete_many({})
        self.service_task = None
        self.broker_connection = await NatsBrokerConnection.connect()

    async def _start_service(self):
        service = ObjectStorageService(broker_connection=self.broker_connection)
        self.service_task = asyncio.create_task(service.run())
        await asyncio.sleep(0.005)

    async def asyncTearDown(self):
        self._db_client.close()
        if self.service_task:
            self.service_task.cancel()
        await self.broker_connection.close()

    async def test_thing_storage(self):
        # this collection_name should be the same as the collection in ObjectStorageService_1.yaml
        self.get_mongo_col(service_id='1', collection_name='things')
        await self._start_service()
        self._db_col.delete_many({})
        for i in range(5):
            thing_msg = Thing(machine='test_machine', name=f'sensor_{i}', measurement_id='123456',
                              value=1, timestamp=datetime(year=2022, month=10, day=10, second=i))

            await self.broker_connection.publish(Thing.get_subject(thing_msg.name), thing_msg)
        await asyncio.sleep(0.02)
        results = self._db_col.find({})
        values = [value for value in results]
        self.assertEqual(values[0]['_subject'], 'v1.thing.sensor_0')

    async def test_object_storage(self):
        self.get_mongo_col(service_id='2', collection_name='custom_test_msg_list')
        self._db_col.delete_many({})
        test_custom_msg_l = CustomTestMsgList(
            values=[CustomTestMsg(x=FIOTTestValue(real=1, img=2),
                                  y=FIOTTestValue(real=1, img=2))])

        await self._start_service()
        await self.broker_connection.publish(test_custom_msg_l.get_subject(), test_custom_msg_l)
        await asyncio.sleep(0.02)
        results = self._db_col.find({})
        values = [value for value in results]
        self.assertEqual(len(values[0]), 4)

    async def test_request_response_thing(self):
        self.get_mongo_col(service_id='1', collection_name='things')
        await self._start_service()
        self._db_col.delete_many({})

        expected_thing_list = []
        for i in range(5):
            thing_msg = Thing(machine='test_machine', name=f'sensor_{i}', measurement_id='123456',
                              value=1, timestamp=datetime(year=2022, month=10, day=9, second=i))
            expected_thing_list.append(thing_msg)
            test_thing_msg_mongo_dict = convert_message_to_mongo_data(
                msg=thing_msg.dict(),
                subject=Thing.get_subject(f'sensor_{i}').name,
                timestamp=datetime(year=2022, month=10, day=9, second=i))
            self._db_col.insert_one(test_thing_msg_mongo_dict)
        hist_req_msg = HistObjectReq(dt_start=datetime(year=2022, month=10, day=9, second=0),
                                     dt_end=datetime(year=2022, month=10, day=9, second=10),
                                     limit=10, subject_name='v1.thing.*',
                                     raw_query={'machine': 'test_machine'})
        subject = hist_req_msg.get_reply_subject(name=filter_specific_sign('thing.*'))

        reply: HistObjectResp = await self.broker_connection.request(subject=subject, msg=hist_req_msg, timeout=10)
        values = [parse_object(v, Thing) for v in reply.values]
        self.assertEqual(expected_thing_list[0], values[0])
        self.assertEqual(len(expected_thing_list), len(values))

    async def test_request_response_object(self):
        self.get_mongo_col(service_id='2', collection_name='custom_test_msg_list')
        await self._start_service()

        expected_object_list = []
        dt_start = datetime.utcnow()
        dt_end = datetime.utcnow() + timedelta(minutes=5)
        for _ in range(5):
            object_msg = CustomTestMsgList(
                values=[CustomTestMsg(x=FIOTTestValue(real=1, img=2),
                                      y=FIOTTestValue(real=1, img=2))])
            expected_object_list.append(object_msg)
            test_object_msg_mongo_dict = convert_message_to_mongo_data(
                msg=object_msg.dict(),
                subject=object_msg.get_subject().name,
                timestamp=datetime.utcnow())
            self._db_col.insert_one(test_object_msg_mongo_dict)

        hist_req_msg = HistObjectReq(dt_start=dt_start, dt_end=dt_end, limit=10,
                                     subject_name=sanitize_pub_subject_name('CustomTestMsgList'))
        reply_subject = hist_req_msg.get_reply_subject(name='custom_test_msg_list')

        reply: HistObjectResp = await self.broker_connection.request(subject=reply_subject, msg=hist_req_msg, timeout=10)
        values = parse_object_list(reply.values, CustomTestMsgList)
        self.assertListEqual(expected_object_list, values)


if __name__ == '__main__':
    unittest.main()
