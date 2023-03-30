import os
from typing import Optional

from fastiot.cli.common.infrastructure_services import TimeScaleDBService
from fastiot.env.env_constants_db import FASTIOT_TIME_SCALE_DB_HOST, FASTIOT_TIME_SCALE_DB_PORT, \
    FASTIOT_TIME_SCALE_DB_USER, FASTIOT_TIME_SCALE_DB_PASSWORD, FASTIOT_TIME_SCALE_DB_DATABASE


class TimeScaleDBEnv:
    """
    Environment variables for timescaledb :class:`fastiot.cli.common.infrastructure_services.TimeScaleDBService`

    Use the properties from :func:`fastiot.env.env.env_timescaledb` to read the values in an easy manner within your
    code.
    """

    @property
    def host(self) -> str:
        """ .. envvar:: FASTIOT_TIME_SCALE_DB_HOST

        Use to get/set the time scale database host. This is usually either ``timescaledb`` within the docker
        network or ``localhost`` when developing against a local time_scale_db.
        """
        return os.getenv(FASTIOT_TIME_SCALE_DB_HOST, 'localhost')

    @property
    def port(self) -> int:
        """ .. envvar:: FASTIOT_TIME_SCALE_DB_PORT

        Use to get/set the time scale db port, defaults to 5432.
        """
        return int(os.getenv(FASTIOT_TIME_SCALE_DB_PORT, TimeScaleDBService().get_default_port()))

    @property
    def user(self) -> Optional[str]:
        """ .. envvar:: FASTIOT_TIME_SCALE_DB_USER

        Use to get/set the TimeScaleDB user.
        """
        return os.getenv(FASTIOT_TIME_SCALE_DB_USER, TimeScaleDBService().get_default_env(FASTIOT_TIME_SCALE_DB_USER))

    @property
    def password(self) -> Optional[str]:
        """ .. envvar:: FASTIOT_TIME_SCALE_DB_PASSWORD

        Use to get/set the time scale db password.
        """
        return os.getenv(FASTIOT_TIME_SCALE_DB_PASSWORD,
                         TimeScaleDBService().get_default_env(FASTIOT_TIME_SCALE_DB_PASSWORD))

    @property
    def database(self) -> str:
        """ .. envvar:: FASTIOT_TIME_SCALE_DB_DATABASE

        Use to get/set the time scale db database.
        """
        return str(os.getenv(FASTIOT_TIME_SCALE_DB_DATABASE,
                             TimeScaleDBService().get_default_env(FASTIOT_TIME_SCALE_DB_DATABASE)))


