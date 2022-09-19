import logging
import sys
import time

from fastiot.env.env import env_influxdb
from fastiot.exceptions import ServiceError


class CustomInfluxClient:
    def __init__(self, db_host: str, db_port: int, db_token: str):

        try:
            # pylint: disable=import-outside-toplevel
            from influxdb_client import InfluxDBClient
            from influxdb_client.client.exceptions import InfluxDBError
        except (ImportError, ModuleNotFoundError):
            logging.error("You have to manually install `influxdb-client>=1.30,<2` using your `requirements.txt` "
                          "to make use of this helper.")
            sys.exit(5)

        sleep_time = 0.2
        num_tries = 300 / sleep_time
        while num_tries > 0:
            try:
                self._db_client = InfluxDBClient(
                    url=f"http://{db_host}:{db_port}",
                    token=db_token,
                    org='IVVDD',
                )
                health_check = self._db_client.ping()
                if health_check:
                    return
                else:
                    continue
            except InfluxDBError:
                time.sleep(0.2)
            num_tries -= 1
        raise ServiceError("Could not connect to InfluxDB")

    def health_check(self) -> bool:
        return self._db_client.ping()


def get_influxdb_client_from_env() -> CustomInfluxClient:
    """
    For connecting Influxdb, the environment variables can be set,
    if you want to use your own settings instead of default:
    :envvar:`FASTIOT_INFLUX_DB_HOST`, :envvar:`FASTIOT_INFLUX_DB_PORT`, :envvar:`FASTIOT_INFLUX_DB_TOKEN`

    >>> influxdb_client = get_influxdb_client_from_env()
    """
    db_client = CustomInfluxClient(
        db_host=env_influxdb.host,
        db_port=env_influxdb.port,
        db_token=env_influxdb.token,
    )
    return db_client
