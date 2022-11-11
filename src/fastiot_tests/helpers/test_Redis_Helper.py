import unittest

from fastiot.core.broker_connection import NatsBrokerConnection
from fastiot.core.serialization import serialize_from_bin
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
        self.assertEqual("1", serialize_from_bin("".__class__, client.get("0")))

    async def test_getData(self):
        helper = RedisHelper(self.broker_connection)
        await helper.sendData(data="1234", source="sensor1")
        data = await helper.getData("0")
        self.assertEqual("1234", data)

    async def test_deleteData(self):
        helper = RedisHelper(self.broker_connection)
        helper.maxDataSets = 3
        for i in range(6):
            await helper.sendData(data="1234", source="sensor1")
        data = await helper.getData("6")
        self.assertEqual(3, len(helper.usedIds))
        self.assertEqual("1234", data)