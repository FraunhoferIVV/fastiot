import os
from typing import Optional

FASTIOT_NATS_LOGGER_FILTER_FIELD = 'FASTIOT_NATS_LOGGER_FILTER_FIELD'
FASTIOT_NATS_LOGGER_FILTER_VALUE = 'FASTIOT_NATS_LOGGER_FILTER_VALUE'
FASTIOT_NATS_LOGGER_SUBJECT = 'FASTIOT_NATS_LOGGER_SUBJECT'


class NatsLoggerConstants:

    @property
    def subject(self) -> str:
        """
        .. envvar:: FASTIOT_NATS_LOGGER_SUBJECT

        Set the subject to listen to. It defaults to ``v1.>`` meaning everything below ``v1``. For more details about
        how to specify (wildcard) subjects please refer to the nats.io documentation at
        https://docs.nats.io/nats-concepts/subjects
        """
        return os.environ.get(FASTIOT_NATS_LOGGER_SUBJECT, 'v1.>')

    @property
    def filter_field(self) -> Optional[str]:
        """
        .. envvar:: FASTIOT_NATS_LOGGER_FILTER_FIELD

        Filter for a specific field, e.g. ``value`` to equal to :envvar:`FASTIOT_NATS_LOGGER_FILTER_VALUE`.
        """
        return os.environ.get(FASTIOT_NATS_LOGGER_FILTER_FIELD)

    @property
    def filter_value(self) -> Optional[str]:
        """
        .. envvar:: FASTIOT_NATS_LOGGER_FILTER_VALUE

        Set the value to filter for.
        """
        return os.environ.get(FASTIOT_NATS_LOGGER_FILTER_VALUE)


nats_logger_env = NatsLoggerConstants()
