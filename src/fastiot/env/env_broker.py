import os

from fastiot.cli.common.infrastructure_services import NatsService
from fastiot.env.env_constants_basic import FASTIOT_NATS_HOST, FASTIOT_NATS_PORT, FASTIOT_NATS_DEFAULT_TIMEOUT


class BrokerEnv:
    """
    Environment variables for the message broker

    Use the properties from :func:`fastiot.env.FASTIOT_NATS_env` to read the values in an easy manner within your
    code.
    """

    @property
    def host(self) -> str:
        """
        .. envvar:: FASTIOT_NATS_HOST

        Use to get/set the broker host. This is usually either ``nats`` within the docker network or ``localhost``
        when developing against a local broker.
        """
        return os.environ.get(FASTIOT_NATS_HOST, 'localhost')

    @property
    def port(self) -> int:
        """
        .. envvar:: FASTIOT_NATS_PORT

        Use to get/set the broker port, defaults to 4222.
        """
        return int(os.getenv(FASTIOT_NATS_PORT, NatsService().get_default_port()))

    @property
    def default_timeout(self) -> float:
        """ .. envvar:: FASTIOT_NATS_DEFAULT_TIMEOUT

        Use to get/set the broker timeout in seconds, defaults to 30.
        """
        return float(os.getenv(FASTIOT_NATS_DEFAULT_TIMEOUT, '30'))


