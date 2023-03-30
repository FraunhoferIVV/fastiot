import os
from typing import Optional

from fastiot.cli.common.infrastructure_services import MariaDBService
from fastiot.env.env_constants_db import FASTIOT_MARIA_DB_HOST, FASTIOT_MARIA_DB_PORT, FASTIOT_MARIA_DB_USER, \
    FASTIOT_MARIA_DB_PASSWORD, FASTIOT_MARIA_DB_SCHEMA_FASTIOTLIB


class MariaDBEnv:
    """
    Environment variables for mariadb :class:`fastiot.cli.common.infrastructure_services.MariaDBService`

    Use the properties from :func:`fastiot.env.env.env_mariadb` to read the values in an easy manner within your
    code. This will provide the environment variables needed for
    :func:`fastiot.db.mariadb_helper_fn.open_mariadb_connection_from_env`
    """

    @property
    def host(self) -> str:
        """ .. envvar:: FASTIOT_MARIA_DB_HOST

        Use to get/set the maria database host. This is usually either ``mariadb`` within the docker network or
        ``localhost`` when developing against a local mariadb.
        """
        return os.getenv(FASTIOT_MARIA_DB_HOST, 'localhost')

    @property
    def port(self) -> int:
        """ .. envvar:: FASTIOT_MARIA_DB_PORT

        Use to get/set the mariadb port, defaults to 3306. """
        return int(os.getenv(FASTIOT_MARIA_DB_PORT, MariaDBService().get_default_port()))

    @property
    def user(self) -> str:
        """ .. envvar:: FASTIOT_MARIA_DB_USER

        Use to get/set the mariadb user.
        """
        return os.getenv(FASTIOT_MARIA_DB_USER, 'root')

    @property
    def password(self) -> Optional[str]:
        """ .. envvar:: FASTIOT_MARIA_DB_PASSWORD

        Use to get/set the mariadb password.
        """
        return os.getenv(FASTIOT_MARIA_DB_PASSWORD, MariaDBService().get_default_env(FASTIOT_MARIA_DB_PASSWORD))

    @property
    def schema_fastiotlib(self) -> str:
        """ .. envvar:: FASTIOT_MARIA_DB_SCHEMA_FASTIOTLIB

        Use to get/set the mariadb schema.
        """
        return str(os.getenv(FASTIOT_MARIA_DB_SCHEMA_FASTIOTLIB))

    @property
    def is_configured(self) -> bool:
        if FASTIOT_MARIA_DB_HOST in os.environ:
            return True
        return False


