import logging
import sys
import time

import aiohttp

from fastiot.env.env import env_influxdb
from fastiot.exceptions import ServiceError


async def get_async_influxdb_client_from_env():
    """
    For connecting Influxdb, the environment variables can be set,
    if you want to use your own settings instead of default:
    :envvar:`FASTIOT_INFLUX_DB_HOST`, :envvar:`FASTIOT_INFLUX_DB_PORT`, :envvar:`FASTIOT_INFLUX_DB_TOKEN`

    >>> influxdb_client = await get_async_influxdb_client_from_env()
    """
    try:
        from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
        from influxdb_client.client.exceptions import InfluxDBError
    except (ImportError, ModuleNotFoundError):
        logging.error("You have to manually install `influxdb-client[async]>=1.30,<2` using your `requirements.txt` "
                      "to make use of this helper.")
        sys.exit(5)

    sleep_time = 0.1
    num_tries = 300 / sleep_time
    while num_tries > 0:
        try:
            client = InfluxDBClientAsync(
                url=f"http://{env_influxdb.host}:{env_influxdb.port}",
                token=env_influxdb.token,
                org='IVVDD'
            )
            health_check = await client.ping()
            if health_check:
                return client
            else:
                num_tries -= 1
                time.sleep(sleep_time)
                continue
        except InfluxDBError:
            time.sleep(sleep_time)
        except aiohttp.ServerDisconnectedError:
            time.sleep(sleep_time)
        except aiohttp.client.ClientConnectorError:
            time.sleep(sleep_time)
