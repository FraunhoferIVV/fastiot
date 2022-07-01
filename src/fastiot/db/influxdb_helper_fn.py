import time

from fastiot.env.env import env_influxdb
from fastiot.exceptions import ServiceError


class CustomInfluxClient:
    def __init__(self, db_host: str, db_port: int, db_token: str):

        from influxdb_client import InfluxDBClient
        from influxdb_client.client.exceptions import InfluxDBError

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
            except InfluxDBError:
                time.sleep(0.2)
            num_tries -= 1
        raise ServiceError("Could not connect to InfluxDB")

    def health_check(self) -> bool:
        return self._db_client.ping()


def get_influxdb_client_from_env() -> CustomInfluxClient:
    db_client = CustomInfluxClient(
        db_host=env_influxdb.host,
        db_port=env_influxdb.port,
        db_token=env_influxdb.token,
    )
    return db_client
