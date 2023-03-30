import os
from typing import Optional

from fastiot.cli.common.infrastructure_services import RedisService
from fastiot.env.env_constants_db import FASTIOT_REDIS_HOST, FASTIOT_REDIS_PORT, FASTIOT_REDIS_PASSWORD


class RedisEnv:
    """ Environment variables to connect to the Redis Server """
    @property
    def host(self) -> str:
        """ .. envvar:: FASTIOT_INFLUX_DB_HOST

        Use to get/set the influx database host. This is usually either ``influxdb`` within the docker network or
        ``localhost`` when developing against a local influxdb.
        """
        return os.getenv(FASTIOT_REDIS_HOST, 'localhost')

    @property
    def port(self) -> int:
        """ .. envvar:: FASTIOT_INFLUX_DB_PORT

        Use to get/set the Redis port, defaults to 8086. """
        return int(os.getenv(FASTIOT_REDIS_PORT, RedisService().get_default_port()))

    @property
    def password(self) -> Optional[str]:
        """ .. envvar:: FASTIOT_REDIS_PASSWORD

        Use to get/set the Redis password.
        """
        return os.getenv(FASTIOT_REDIS_PASSWORD,
                         RedisService().get_default_env(FASTIOT_REDIS_PASSWORD))


