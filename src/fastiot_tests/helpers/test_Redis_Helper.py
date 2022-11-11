import unittest

from fastiot.core.broker_connection import NatsBrokerConnection
from fastiot.core.serialization import serialize_from_bin
from fastiot.helpers.redis_helper import getRedisClient, RedisHelper
from fastiot.msg.thing import RedisMsg
from fastiot.testlib import populate_test_env



class TestRedisHelper(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        populate_test_env()
        self.broker_connection = await NatsBrokerConnection.connect()
        await RedisHelper(self.broker_connection).deleteall()

    async def test_connection(self):
        client = await getRedisClient()
        self.assertTrue(client.ping())

    async def test_sendData(self):
        helper = RedisHelper(self.broker_connection)
        client = await getRedisClient()
        subject = RedisMsg.get_subject("sensor1")
        await helper.send_data(data="1", subject=subject)
        self.assertEqual("1", serialize_from_bin("".__class__, client.get("0")))

    async def test_getData(self):
        helper = RedisHelper(self.broker_connection)
        subject = RedisMsg.get_subject("sensor1")
        await helper.send_data(data="12345", subject=subject)
        helper = RedisHelper(self.broker_connection)
        data = await helper.get_data("0")
        self.assertEqual("12345", data)

    async def test_deleteData(self):
        helper = RedisHelper(self.broker_connection)
        helper.maxDataSets = 3
        for i in range(6):
            subject = RedisMsg.get_subject(f"sensor{i}")
            await helper.send_data(data="1234", subject=subject)
        data = await helper.get_data("4")
        self.assertEqual(3, len(helper.usedIds))
        self.assertEqual("1234", data)