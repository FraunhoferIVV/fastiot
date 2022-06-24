""" Module to hold basic environment variables """
import os


FASTIOT_BROKER_HOST = 'FASTIOT_BROKER_HOST'
FASTIOT_BROKER_PORT = 'FASTIOT_BROKER_PORT'
FASTIOT_BROKER_DEFAULT_TIMEOUT = 'FASTIOT_BROKER_DEFAULT_TIMEOUT'
FASTIOT_BROKER_STREAM_TIMEOUT = 'FASTIOT_BROKER_STREAM_TIMEOUT'


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


fastiot_broker_env = BrokerEnv()
