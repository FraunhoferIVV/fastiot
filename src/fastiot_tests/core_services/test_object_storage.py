import asyncio
import unittest
from datetime import datetime
from typing import List

from pydantic import BaseModel

from fastiot.core.broker_connection import NatsBrokerConnectionImpl
from fastiot.core.data_models import FastIoTData, Subject
from fastiot.db.mongodb_helper_fn import get_mongodb_client_from_env
from fastiot.env import env_mongodb
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
        self.broker_connection = await NatsBrokerConnectionImpl.connect()
        service = FastIoTTestService(broker_connection=self.broker_connection)
        self.service_task = asyncio.create_task(service.run())

    async def _start_service(self):
        service = ObjectStorageService(broker_connection=self.broker_connection)
        self.service_task = asyncio.create_task(service.run())
        await asyncio.sleep(0.005)

    async def asyncTearDown(self):
        self.service_task.cancel()

    @unittest.skip('')
    def test_thing_dict_to_mongo(self):
        thing_msg = Thing(machine='test_machine', name='test_thing', measurement_id='123456',
                          value=1, timestamp=datetime(year=2022, month=10, day=10, second=1))
        test_thing_msg_mongo_dict = convert_message_to_mongo_data(thing_msg.dict())
        self.assertEqual('123456', test_thing_msg_mongo_dict['Object']['measurement_id'])
        self._db_col.insert_one(test_thing_msg_mongo_dict)

    @unittest.skip('')
    async def test_thing_storage(self):
        thing_msg = Thing(machine='test_machine', name='test_thing', measurement_id='123456',
                          value=1, timestamp=datetime(year=2022, month=10, day=10, second=1))

        await self._start_service()
        await self.broker_connection.publish(Thing.get_subject(), thing_msg)
        await asyncio.sleep(0.02)


    @unittest.skip('')
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

    #@unittest.skip('')
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

