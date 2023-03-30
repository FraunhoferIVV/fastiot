import os
from typing import Optional

from fastiot.cli.common.infrastructure_services import MongoDBService
from fastiot.env.env_constants_db import FASTIOT_MONGO_DB_HOST, FASTIOT_MONGO_DB_PORT, FASTIOT_MONGO_DB_USER, \
    FASTIOT_MONGO_DB_PASSWORD, FASTIOT_MONGO_DB_AUTH_SOURCE, FASTIOT_MONGO_DB_NAME, FASTIOT_MONGO_DB_MEM_LIMIT, \
    FASTIOT_MONGO_DB_TIME_SERIES_COL


class MongoDBEnv:
    """
    Environment variables for mongodb :class:`fastiot.cli.common.infrastructure_services.MongoDBService`

    Use the properties from :func:`fastiot.env.env.env_mongodb` to read the values in an easy manner within your
    code.
    """

    @property
    def host(self) -> str:
        """ .. envvar:: FASTIOT_MONGO_DB_HOST

        Use to get/set the mongo database host. This is usually either ``mongodb`` within the docker network or
        ``localhost`` when developing against a local mongodb.
        """
        return os.getenv(FASTIOT_MONGO_DB_HOST, 'localhost')

    @property
    def port(self) -> int:
        """ .. envvar:: FASTIOT_MONGO_DB_PORT

        Use to get/set the mongodb port, defaults to 27017. """
        return int(os.getenv(FASTIOT_MONGO_DB_PORT, MongoDBService().get_default_port()))

    @property
    def user(self) -> Optional[str]:
        """ .. envvar:: FASTIOT_MONGO_DB_USER

        Use to get/set the mongodb user.
        """
        return os.getenv(FASTIOT_MONGO_DB_USER, MongoDBService().get_default_env(FASTIOT_MONGO_DB_USER))

    @property
    def password(self) -> Optional[str]:
        """ .. envvar:: FASTIOT_MONGO_DB_PASSWORD

        Use to get/set the mongodb password.
        """
        return os.getenv(FASTIOT_MONGO_DB_PASSWORD, MongoDBService().get_default_env(FASTIOT_MONGO_DB_PASSWORD))

    @property
    def auth_source(self) -> Optional[str]:
        """ .. envvar:: FASTIOT_MONGO_DB_AUTH_SOURCE

        Use to get/set the mongodb auth source, which is a database name which is needed for authentication.
        """
        return os.getenv(FASTIOT_MONGO_DB_AUTH_SOURCE, 'admin')

    @property
    def name(self) -> str:
        """ .. envvar:: FASTIOT_MONGO_DB_NAME

        Use to get/set the name of mongodb database.
        """
        return os.getenv(FASTIOT_MONGO_DB_NAME, "fastiot")

    @property
    def mem_limit(self) -> str:
        return os.getenv(FASTIOT_MONGO_DB_MEM_LIMIT, "256m")

    @property
    def is_configured(self) -> bool:
        """
        Use to indicate if the mongodb is configured, it is not bound to any environment variable
        """
        if FASTIOT_MONGO_DB_HOST in os.environ:
            return True
        return False


class MongoDBColConstants:
    """
    Environment variables for mongodb collection

    Use the properties from :func:`fastiot.env.env_mongodb_cols` to read the values in an easy manner within your
    code.
    """
    @property
    def time_series(self) -> str:
        """ ..envvar:: FASTIOT_MONGO_DB_TIME_SERIES_COL

        """
        return os.getenv(FASTIOT_MONGO_DB_TIME_SERIES_COL, 'time_series')


