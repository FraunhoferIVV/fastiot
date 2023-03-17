import asyncio
import os
import unittest
from datetime import datetime, timedelta, timezone
from typing import List, Type, Union

from pydantic import BaseModel

from fastiot.core.broker_connection import NatsBrokerConnection
from fastiot.core.data_models import FastIoTData, FastIoTPublish
from fastiot.core.subject_helper import sanitize_pub_subject_name, filter_specific_sign
from fastiot.db.mongodb_helper_fn import get_mongodb_client_from_env
from fastiot.env import env_mongodb, FASTIOT_SERVICE_ID
from fastiot.msg.custom_db_data_type_conversion import to_mongo_data
from fastiot.msg.hist import HistObjectReq, HistObjectResp
from fastiot.msg.thing import Thing
from fastiot.testlib import populate_test_env
from fastiot.util.object_helper import parse_object, parse_object_list
from fastiot_core_services.object_storage.mongodb_handler import MongoDBHandler
from fastiot_core_services.object_storage.object_storage_service import ObjectStorageService

THING = Thing(machine='SomeMachine', name="RequestSensor", value=42, timestamp=datetime.now(), measurement_id="1")

"""
test thing overwriting with the following file: 
sensor_1 sensor_2 measurement_id timestamp
thing0 thing1 1 t1
thing2 thing3 1 t2
thing4 thing5 2 t2
Converted to messages row by row
Publish MESSAGES to the message broker
"""
MESSAGES = [Thing(machine='test_machine', name='sensor_1', measurement_id='79438k',
                  value=5, timestamp=datetime(year=2023, month=3, day=16, microsecond=1000)),
            Thing(machine='test_machine', name='sensor_2', measurement_id='79438k',
                  value=True, timestamp=datetime(year=2023, month=3, day=16, microsecond=1000)),
            Thing(machine='test_machine', name='sensor_1', measurement_id='79438k',
                  value=15, timestamp=datetime(year=2023, month=3, day=16, microsecond=7000)),
            Thing(machine='test_machine', name='sensor_2', measurement_id='79438k',
                  value=False, timestamp=datetime(year=2023, month=3, day=16, microsecond=7000)),
            Thing(machine='test_machine', name='sensor_1', measurement_id='79438d',
                  value=25.3, timestamp=datetime(year=2023, month=3, day=16, microsecond=7000)),
            Thing(machine='test_machine', name='sensor_2', measurement_id='79438d',
                  value='Unknown', timestamp=datetime(year=2023, month=3, day=16, microsecond=7000))
            ]


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
        values = list(results)
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
                timestamp=datetime(year=2022, month=10, day=9, second=i, tzinfo=timezone.utc))
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

        reply: HistObjectResp = await self.broker_connection.request(subject=reply_subject, msg=hist_req_msg,
                                                                     timeout=10)
        values = parse_object_list(reply.values, CustomTestMsgList)
        self.assertListEqual(expected_object_list, values)

    async def test_overwriting_thing_no_change(self):
        self.get_mongo_col(service_id='u1', collection_name='thing')
        await self._start_service()
        self._db_col.delete_many({})
        # send messages
        for msg in MESSAGES:
            await self.broker_connection.publish(Thing.get_subject(msg.name), msg)
        await asyncio.sleep(0.02)
        # check if all objects have been inserted
        results = list(self._db_col.find({}))
        self.assertEqual(len(MESSAGES), len(results))
        # send messages one more time
        for msg in MESSAGES:
            await self.broker_connection.publish(Thing.get_subject(msg.name), msg)
        await asyncio.sleep(0.02)
        # check if results are still the same
        results1 = list(self._db_col.find({}))
        self.assertListEqual(results, results1)

    async def test_overwriting_thing_only_change(self):
        self.get_mongo_col(service_id='u1', collection_name='thing')
        await self._start_service()
        self._db_col.delete_many({})
        # send messages
        for msg in MESSAGES:
            await self.broker_connection.publish(Thing.get_subject(msg.name), msg)
        await asyncio.sleep(0.02)
        # modify messages
        messages = MESSAGES.copy()
        for idx, msg in enumerate(messages):
            msg.value = idx*7
        # send modified messages
        for msg in messages:
            await self.broker_connection.publish(Thing.get_subject(msg.name), msg)
        await asyncio.sleep(0.02)
        # check results
        results = list(self._db_col.find({}))
        self.assertEqual(len(MESSAGES), len(results))
        self.assertEqual(21, results[3]['value'])

    async def test_overwriting_thing_add_data(self):
        self.get_mongo_col(service_id='u1', collection_name='thing')
        await self._start_service()
        self._db_col.delete_many({})
        # send messages
        for msg in MESSAGES:
            await self.broker_connection.publish(Thing.get_subject(msg.name), msg)
        await asyncio.sleep(0.02)
        # modify messages (add new things)
        messages = MESSAGES.copy()
        messages += [Thing(machine='test_machine', name='sensor_1', measurement_id='8000e',
                           value=35, timestamp=datetime(year=2023, month=3, day=16, microsecond=9000)),
                     Thing(machine='test_machine', name='sensor_2', measurement_id='8000e',
                           value=True, timestamp=datetime(year=2023, month=3, day=16, microsecond=9000))]
        # send modified messages
        for msg in messages:
            await self.broker_connection.publish(Thing.get_subject(msg.name), msg)
        await asyncio.sleep(0.02)
        # check results
        results = list(self._db_col.find({}))
        self.assertEqual(len(messages), len(results))
        self.assertEqual(35, results[len(MESSAGES)]['value'])
        self.assertEqual(True, results[len(MESSAGES) + 1]['value'])

    async def test_overwriting_thing_changed_data(self):
        self.get_mongo_col(service_id='u1', collection_name='thing')
        await self._start_service()
        self._db_col.delete_many({})
        # send messages
        for msg in MESSAGES:
            await self.broker_connection.publish(Thing.get_subject(msg.name), msg)
        await asyncio.sleep(0.02)
        # modify messages (update things, removing mustn't affect results)
        messages = MESSAGES.copy()
        messages[5].value = True
        messages[0].value = 0.005
        messages[0].unit = 'k'
        messages[4].value = 'Error'
        del messages[2:4]
        # send modified messages
        for msg in messages:
            await self.broker_connection.publish(Thing.get_subject(msg.name), msg)
        await asyncio.sleep(0.02)
        # check results
        results = list(self._db_col.find({}))
        self.assertEqual(len(MESSAGES), len(results))
        self.assertEqual(True, results[5]['value'])
        self.assertEqual(0.005, results[0]['value'])
        self.assertEqual('k', results[0]['unit'])
        self.assertEqual('Error', results[4]['value'])
        self.assertEqual('v1.thing.sensor_1', results[2]['_subject'])
        self.assertEqual(15, results[2]['value'])
        self.assertEqual('v1.thing.sensor_2', results[3]['_subject'])
        self.assertEqual(False, results[3]['value'])

    async def test_overwriting_thing_combined(self):
        self.get_mongo_col(service_id='u1', collection_name='thing')
        await self._start_service()
        self._db_col.delete_many({})
        # send messages
        for msg in MESSAGES:
            try:
                await self.broker_connection.publish(Thing.get_subject(msg.name), msg)
                await asyncio.sleep(0.002)
            except RuntimeError:
                pass
        await asyncio.sleep(0.02)
        # modify messages
        messages = MESSAGES.copy()
        # 1 inserting new things (identified as new)
        messages.insert(2, Thing(machine='test_machine', name='sensor_1', measurement_id='8000e',
                                 value=35, timestamp=datetime(year=2023, month=3, day=16, microsecond=9000)))
        messages.insert(3, Thing(machine='test_machine', name='sensor_2', measurement_id='8000e',
                                 value=True, timestamp=datetime(year=2023, month=3, day=16, microsecond=9000)))
        # 2 changing old things (if primary key changed then almost the same as inserting a new thing)
        messages[0].value = 0.005
        messages[0].unit = 'k'
        messages[0].measurement_id = messages[1].measurement_id = '56341f'
        messages[6].value = 'Error'
        messages[7].value = True
        # 3 deleting old things
        del messages[4:6]
        # send modified messages
        for msg in messages:
            try:
                await self.broker_connection.publish(Thing.get_subject(msg.name), msg)
                await asyncio.sleep(0.002)
            except RuntimeError:
                pass
        # check results
        results = list(self._db_col.find({}))
        self.assertEqual(10, len(results))
        self.assertEqual(35, results[8]['value'])
        self.assertEqual(True, results[9]['value'])
        self.assertEqual(True, results[5]['value'])
        self.assertEqual(0.005, results[6]['value'])
        self.assertEqual('k', results[6]['unit'])
        self.assertEqual('Error', results[4]['value'])
        self.assertEqual('v1.thing.sensor_1', results[2]['_subject'])
        self.assertEqual(15, results[2]['value'])
        self.assertEqual('v1.thing.sensor_2', results[3]['_subject'])
        self.assertEqual(False, results[3]['value'])

    async def test_overwriting_object_no_change(self):
        self.get_mongo_col(service_id='u2', collection_name='custom_test_msg_list')
        await self._start_service()
        self._db_col.delete_many({})
        messages = []
        for i in range(1, 6):
            msg_list = [CustomTestMsg(x=FIOTTestValue(real=i, img=2*i),
                                      y=FIOTTestValue(real=3*i, img=4*i))]
            test_custom_msg_list = CustomTestMsgList(values=msg_list)
            messages.append(test_custom_msg_list)
        # send
        for msg in messages:
            await self.broker_connection.publish(msg.get_subject(), msg)
        await asyncio.sleep(0.02)
        # check if all objects have been inserted
        results = list(self._db_col.find({}))
        self.assertEqual(5, len(results))
        # send once more
        for msg in messages:
            await self.broker_connection.publish(msg.get_subject(), msg)
        await asyncio.sleep(0.02)
        # check results
        self.assertEqual(5, len(results))

if __name__ == '__main__':
    unittest.main()
