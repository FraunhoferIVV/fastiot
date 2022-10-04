import unittest

from fastiot.db.influxdb_helper_fn import get_async_influxdb_client_from_env
from fastiot.db.mariadb_helper_fn import open_mariadb_connection_from_env, init_schema
from fastiot.db.mongodb_helper_fn import get_mongodb_client_from_env
from fastiot.db.time_scale_helper_fn import open_timescaledb_connection_from_env


class TestDataBases(unittest.TestCase):
    def test_mongo_db_connection(self):
        client_wrapper = get_mongodb_client_from_env()
        self.assertTrue(client_wrapper.health_check())

    def test_mariadb_connection(self):
        db_connection = open_mariadb_connection_from_env(schema=None)
        init_schema(connection=db_connection, schema='fastiot_fastiotlib')
        self.assertTrue('MariaDB' in db_connection.get_server_info())

    def test_timescaledb_connection(self):
        db_connection = open_timescaledb_connection_from_env()
        self.assertIsNotNone(db_connection.server_version)


class TestDataBasesAsync(unittest.IsolatedAsyncioTestCase):

    async def test_async_influxdb_connection(self):
        db_client = await get_async_influxdb_client_from_env()
        self.assertTrue(await db_client.ping())
        await db_client.close()


if __name__ == '__main__':
    unittest.main()
