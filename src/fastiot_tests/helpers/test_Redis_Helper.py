import unittest

from fastiot.core.broker_connection import NatsBrokerConnection
from fastiot.helpers.Redis_Helper import getRedisClient, RedisHelper
from fastiot.testlib import populate_test_env



class TestRedisHelper(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        populate_test_env()
        self.broker_connection = await NatsBrokerConnection.connect()

    async def test_connection(self):
        client = await getRedisClient()
        self.assertTrue(client.ping())

    async def test_sendData(self):
        helper = RedisHelper(self.broker_connection)
        client = await getRedisClient()
        await helper.sendData(data="1", source="sensor1")
        self.assertEqual("1", client.get("0").decode("ascii"))

    async def test_getData(self):
        helper = RedisHelper(self.broker_connection)
        client = await getRedisClient()
        await helper.sendData(data="1234", source="sensor1")
        data = await helper.getData("0")
        self.assertEqual("1234", data.decode("ascii"))

    async def test_deleteData(self):
        helper = RedisHelper(self.broker_connection)
        client = await getRedisClient()
        for i in range(50):
            await helper.sendData(data="1234", source="sensor1")
        data = await helper.getData("0")
        self.assertEqual(10, len(helper.usedIds))
        self.assertEqual("1234", data.decode("ascii"))