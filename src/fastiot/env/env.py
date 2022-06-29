""" Module to hold basic environment variables """
import os
from typing import Optional

from fastiot.env.env_constants import *


class BasicEnv:
    """
    Holds the default environment variables for the fastIoT framework.

    Use the properties from :func:`fastiot.env.fastiot_basic_env` to read the values in an easy manner within your code.
    """

    @property
    def config_dir(self):
        """ .. envvar:: FASTIOT_CONFIG_DIR

        Use to set/get the config dir, defaults to :file:`/etc/fastiot` if not set.

        This should point to your deployment configuration dir, which is also copied to target either manually or using
        the :func:`fastiot.cli.commands.deploy.deploy` CLI command.

        This variable is either handled in your container or can be overwritten using e.g. a
        :file:`local-testing-overwrite.env` in your config-dir. See the Tutorial :ref:`label-setting-up-pycharm` for
        more details about setting env vars within PyCharm.

        On automatic project setups everything should work out fine for you!
        """
        return os.getenv(FASTIOT_CONFIG_DIR, '/etc/fastiot')


class BrokerEnv:
    """
    Environment variables for the message broker

    Use the properties from :func:`fastiot.env.fastiot_broker_env` to read the values in an easy manner within your
    code.
    """

    @property
    def host(self) -> str:
        """ .. envvar:: FASTIOT_BROKER_HOST
        Use to get/set the broker host. This is usually either ``nats`` within the docker network or ``localhost``
        when developing against a local broker."""
        return os.environ[FASTIOT_BROKER_HOST]

    @property
    def port(self) -> int:
        """ .. envvar:: FASTIOT_BROKER_HOST
        Use to get/set the broker port, defaults to 4222. """
        return int(os.getenv(FASTIOT_BROKER_PORT, '4222'))

    @property
    def default_timeout(self) -> float:
        """ .. envvar:: FASTIOT_BROKER_DEFAULT_TIMEOUT
        Use to get/set the broker timeout in seconds, defaults to 30. """
        return float(os.getenv(FASTIOT_BROKER_DEFAULT_TIMEOUT, '30'))

    @property
    def stream_timeout(self) -> float:
        """ .. envvar::FASTIOT_BROKER_STREAM_TIMEOUT
        Use to get/set  the broker stream timeout in seconds, defaults to 10. """
        return float(os.getenv(FASTIOT_BROKER_STREAM_TIMEOUT, '10'))


env_basic = BasicEnv()
env_broker = BrokerEnv()
