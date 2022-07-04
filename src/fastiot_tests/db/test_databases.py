import unittest

from fastiot.db.mongodb_helper_fn import get_mongodb_client_from_env
from fastiot.db.influxdb_helper_fn import get_influxdb_client_from_env
from fastiot.db.mariadb_helper_fn import open_mariadb_connection_from_env
from fastiot.db.time_scale_helper_fn import open_timescaledb_connection_from_env
from fastiot_tests.test_env import populate_db_test_env


class TestMongoDB(unittest.TestCase):

    @unittest.skip('Waiting for corresponding docker-compose')
    def test_connection(self):
        populate_db_test_env()

        db_client = get_mongodb_client_from_env()
        self.assertTrue(db_client.health_check())


class TestMariaDB(unittest.TestCase):

    @unittest.skip('Waiting for corresponding docker-compose')
    def test_connection(self):
        populate_db_test_env()

        db_connection = open_mariadb_connection_from_env(schema='fastiot_fastiotlib')
        self.assertTrue('MariaDB' in db_connection.get_server_info())


class TestInfluxDB(unittest.TestCase):

    @unittest.skip('Waiting for corresponding docker-compose')
    def test_connection(self):
        populate_db_test_env()

        db_client = get_influxdb_client_from_env()
        self.assertTrue(db_client.health_check())


class TestTimeScaleDB(unittest.TestCase):

    @unittest.skip('Waiting for corresponding docker-compose')
    def test_connection(self):
        populate_db_test_env()

        db_connection = open_timescaledb_connection_from_env()
        self.assertIsNotNone(db_connection.server_version)


if __name__ == '__main__':
    unittest.main()
