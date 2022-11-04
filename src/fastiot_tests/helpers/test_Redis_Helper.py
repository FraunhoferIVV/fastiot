import unittest

from fastiot.helpers.Redis_Helper import RedisClient
from fastiot.testlib import populate_test_env



class TestRedisHelper(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        populate_test_env()

    async def test_connection(self):

        r = RedisClient()
        self.assertTrue(await r.connect())
