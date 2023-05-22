import logging
import os

from fastiot.env.env_constants_basic import FASTIOT_CONFIG_DIR, FASTIOT_LOG_LEVEL, FASTIOT_VOLUME_DIR, \
    FASTIOT_SERVICE_ID, FASTIOT_USE_INTERNAL_HOSTNAMES
from fastiot.env.helpers import parse_bool_flag


class BasicEnv:
    """
    Holds the default environment variables for the fastIoT framework.

    Use the properties from :func:`fastiot.env.fastiot_basic_env` to read the values in an easy manner within your code.
    """

    @property
    def config_dir(self):
        """ .. envvar:: FASTIOT_CONFIG_DIR

        Use to get the config dir, defaults to :file:`/etc/fastiot` if not set.

        Usually, you don't need to specify this variable manually, instead use config-dir entry on deployments. This
        way, this variable is automatically injected.

        On automatic project setups everything should work out fine for you!
        """
        return os.getenv(FASTIOT_CONFIG_DIR, '/etc/fastiot')

    @property
    def log_level(self) -> int:
        """ .. envvar:: FASTIOT_LOG_LEVEL

        This environment variable is used to set the logging Level. Defaults to Info-Level (=20)
        Level for logging s. https://docs.python.org/3/library/logging.html#logging-levels
        """
        if FASTIOT_LOG_LEVEL not in os.environ:
            return logging.INFO

        try:
            return int(os.environ[FASTIOT_LOG_LEVEL])
        except:
            pass

        try:
            return int(logging.getLevelName(os.environ[FASTIOT_LOG_LEVEL].upper()))
        except:
            pass

        raise ValueError(
            f"Env variable '{FASTIOT_LOG_LEVEL}' is set to '{os.environ[FASTIOT_LOG_LEVEL]}' "
            "which is not a valid log level."
        )

    @property
    def volume_dir(self) -> str:
        """ .. envvar:: FASTIOT_VOLUME_DIR

        Use this variable to set the default mount dir for your project
        """
        return os.getenv(FASTIOT_VOLUME_DIR, '/var/fastiot')

    @property
    def service_id(self) -> str:
        """ .. envvar:: FASTIOT_SERVICE_ID

        Use this variable to differentiate between multiple instances of the same service. The result is available as
        ``self.service_id``. It is for example used to read a configuration file for each service with
        :func:`fastiot.util.config_helper.read_config`. See :ref:`configuration_for_service` for more information.
        """
        return os.getenv(FASTIOT_SERVICE_ID, '')

    @property
    def log_dir(self) -> str:
        return os.path.join(self.volume_dir, 'logs')

    @property
    def error_logfile(self) -> str:
        return os.path.join(self.log_dir, 'error.log')


class TestsEnv:
    """
    Environment variables for running tests
    """

    @property
    def use_internal_hostnames(self) -> bool:
        """  .. envvar:: FASTIOT_USE_INTERNAL_HOSTNAMES

        When starting containers inside another container, e.g. within a Jenkins running in a docker we cannot use
        ``localhost`` as hostname but need to use the docker container names as hast, e.g. ``nats``.
        Set this to True, to enable this method!
        """
        return parse_bool_flag(FASTIOT_USE_INTERNAL_HOSTNAMES, False)
