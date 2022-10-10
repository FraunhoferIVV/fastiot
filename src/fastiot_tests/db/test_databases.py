import unittest

from fastiot.db.influxdb_helper_fn import get_async_influxdb_client_from_env
from fastiot.db.mariadb_helper_fn import get_mariadb_client_from_env, init_schema
from fastiot.db.mongodb_helper_fn import get_mongodb_client_from_env
from fastiot.db.time_scale_helper_fn import get_timescaledb_client_from_env
from fastiot.testlib import populate_test_env


class TestDataBases(unittest.TestCase):
    def setUp(self):
        populate_test_env()

    def test_mongo_db_connection(self):
        db_client = get_mongodb_client_from_env()
        self.assertTrue(db_client.admin.command('ping'))

    def test_mariadb_connection(self):
        db_client = get_mariadb_client_from_env(schema=None)
        init_schema(connection=db_client, schema='fastiot_fastiotlib')
        self.assertTrue('MariaDB' in db_client.get_server_info())

    def test_timescaledb_connection(self):
        db_client = get_timescaledb_client_from_env()
        self.assertIsNotNone(db_client.server_version)


class TestDataBasesAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        populate_test_env()

    @unittest.skip("Not working atm")
    async def test_async_influxdb_connection(self):
        populate_test_env()

        db_client = await get_async_influxdb_client_from_env()
        self.assertTrue(await db_client.ping())
        await db_client.close()


if __name__ == '__main__':
    unittest.main()
