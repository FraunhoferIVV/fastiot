import os

from fastiot.cli.common.infrastructure_services import InfluxDBService
from fastiot.env.env_constants_db import FASTIOT_INFLUX_DB_HOST, FASTIOT_INFLUX_DB_PORT, FASTIOT_INFLUX_DB_USER, \
    FASTIOT_INFLUX_DB_PASSWORD, FASTIOT_INFLUX_DB_ORG, FASTIOT_INFLUX_DB_BUCKET, FASTIOT_INFLUX_DB_TOKEN


class InfluxDBEnv:
    """
    Environment variables for influxdb :class:`fastiot.cli.common.infrastructure_services.InfluxDBService`

    Use the properties from :func:`fastiot.env.env.env_influxdb` to read the values in an easy manner within your
    code. For connecting to InfluxDB, which is started with a token, you only need host, port and token.
    username and password are used for browser GUI.
    """

    @property
    def host(self) -> str:
        """ .. envvar:: FASTIOT_INFLUX_DB_HOST

        Use to get/set the influx database host. This is usually either ``influxdb`` within the docker network or
        ``localhost`` when developing against a local influxdb.
        """
        return os.getenv(FASTIOT_INFLUX_DB_HOST, 'localhost')

    @property
    def port(self) -> int:
        """ .. envvar:: FASTIOT_INFLUX_DB_PORT

        Use to get/set the influxdb port, defaults to 8086. """
        return int(os.getenv(FASTIOT_INFLUX_DB_PORT, InfluxDBService().get_default_port()))

    @property
    def user(self) -> str:
        """ .. envvar:: FASTIOT_INFLUX_DB_USER

        Use to get/set the influxdb username, default to 'influx_db_admin'.
        This env var is only used for browser login, not for connecting from fastiot framework.
        """
        return str(os.getenv(FASTIOT_INFLUX_DB_USER, 'influx_db_admin'))

    @property
    def password(self) -> str:
        """ .. envvar:: FASTIOT_INFLUX_DB_PASSWORD

        Use to get/set the influxdb password, default to 'mf9ZXfeLKuaL3HL7w'.
        This env var is only used for browser login, not for connecting from fastiot framework.
        password for InfluxDB must be complex, otherwise InfluxDB won't be started.
        """
        return str(os.getenv(FASTIOT_INFLUX_DB_PASSWORD, InfluxDBService().get_default_env(FASTIOT_INFLUX_DB_PASSWORD)))

    @property
    def token(self) -> str:
        """.. envvar:: FASTIOT_INFLUX_DB_TOKEN

        InfluxDB API token with permission to query (read) buckets and create (write) authorizations for devices
        """
        return os.getenv(FASTIOT_INFLUX_DB_TOKEN, InfluxDBService().get_default_env(FASTIOT_INFLUX_DB_TOKEN))

    @property
    def organisation(self) -> str:
        """ .. envvar:: FASTIOT_INFLUX_DB_ORG

        Set the organisation for InfluxDB, defaults to ``FastIoT`` if not set.
        """
        return os.environ.get(FASTIOT_INFLUX_DB_ORG, InfluxDBService().get_default_env(FASTIOT_INFLUX_DB_ORG))

    @property
    def bucket(self) -> str:
        """ .. envvar:: FASTIOT_INFLUX_DB_BUCKET

        Set the bucket for InfluxDB to store data, defaults to ``things`` if not set.
        """
        return os.environ.get(FASTIOT_INFLUX_DB_BUCKET, InfluxDBService().get_default_env(FASTIOT_INFLUX_DB_BUCKET))


