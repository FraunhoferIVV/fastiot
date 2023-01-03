import os
from enum import Enum

from fastiot.env import env_basic

FASTIOT_OPCUA_ENDPOINT_URL = 'FASTIOT_OPCUA_ENDPOINT_URL'
FASTIOT_OPCUA_SECURITY_STRING = 'FASTIOT_OPCUA_SECURITY_STRING'
FASTIOT_OPCUA_USER = 'FASTIOT_OPCUA_USER'
FASTIOT_OPCUA_PASSWORD = 'FASTIOT_OPCUA_PASSWORD'
FASTIOT_OPCUA_APPLICATION_URI = 'FASTIOT_OPCUA_APPLICATION_URI'
FASTIOT_OPCUA_MAX_ALLOWED_DATA_DELAY = 'FASTIOT_OPCUA_MAX_ALLOWED_DATA_DELAY'
FASTIOT_OPCUA_RETRIEVAL_MODE = 'FASTIOT_OPCUA_RETRIEVAL_MODE'
FASTIOT_OPCUA_POLLING_DELAY = 'FASTIOT_OPCUA_POLLING_DELAY'
FASTIOT_MACHINE_MONITORING_CONFIG_NAME = 'FASTIOT_MACHINE_MONITORING_CONFIG_NAME'
FASTIOT_MACHINE_MONITORING_ERROR_LOGFILE = 'FASTIOT_MACHINE_MONITORING_ERROR_LOGFILE'


class OPCUARetrievalMode(str, Enum):
    subscription = 'subscription'
    polling = 'polling'
    polling_always = 'polling_always'


class OPCUAEnv:
    """
    Environment variables for opc ua monitoring
    """

    @property
    def endpoint_url(self) -> str:
        """ .. envvar:: FASTIOT_OPCUA_ENDPOINT_URL
        """
        return os.environ[FASTIOT_OPCUA_ENDPOINT_URL]

    @property
    def security_string(self) -> str:
        """ .. envvar:: FASTIOT_OPCUA_SECURITY_STRING
        """
        return os.getenv(FASTIOT_OPCUA_SECURITY_STRING, '')

    @property
    def user(self) -> str:
        """ .. envvar:: FASTIOT_OPCUA_USER
        """
        return os.getenv(FASTIOT_OPCUA_USER, '')

    @property
    def password(self) -> str:
        """ .. envvar:: FASTIOT_OPCUA_PASSWORD
        """
        return os.getenv(FASTIOT_OPCUA_PASSWORD, '')

    @property
    def application_uri(self) -> str:
        """ .. envvar:: FASTIOT_OPCUA_APPLICATION_URI
        """
        return os.getenv(FASTIOT_OPCUA_APPLICATION_URI, '')

    @property
    def max_allowed_data_delay(self) -> float:
        """
        .. envvar:: FASTIOT_OPCUA_MAX_ALLOWED_DATA_DELAY

        The maximum allowed data delay for opc-ua connections in seconds. If no data changes happen over this timespan,
        the connection to the machine is considered lost. This value must be positive. A value of zero means the
        connection is never considered lost.
        """
        value = float(os.getenv(FASTIOT_OPCUA_MAX_ALLOWED_DATA_DELAY, "0.0"))
        if value < 0.0:
            raise ValueError(
                'Environment variable "FASTIOT_OPCUA_MAX_ALLOWED_DATA_DELAY" is negative which is invalid.'
            )
        return value

    @property
    def polling_delay(self) -> float:
        """
        .. envvar:: FASTIOT_OPCUA_POLLING_DELAY

        The polling delay specifies the delay between polling opcua node cycles. This value is only applied if retrieval
        mode is polling, which is the default behavior, or polling_always. Otherwise this variable is ignored. Must be
        positive. A value of zero means no wait interval which may result in high server load.
        """
        value = float(os.getenv(FASTIOT_OPCUA_POLLING_DELAY, "0.2"))
        if value < 0.0:
            raise ValueError(
                'Environment variable "FASTIOT_OPCUA_POLLING_DELAY" is negative which is invalid.'
            )
        return value

    @property
    def retrieval_mode(self) -> OPCUARetrievalMode:
        """ .. envvar:: FASTIOT_OPCUA_RETRIEVAL_MODE
        """
        return OPCUARetrievalMode(os.getenv(FASTIOT_OPCUA_RETRIEVAL_MODE, OPCUARetrievalMode.polling))

    @property
    def machine_monitoring_config_dir(self) -> str:
        """ .. envvar:: FASTIOT_MACHINE_MONITORING_CONFIG_NAME
        """
        config_dir_relative = os.getenv(FASTIOT_MACHINE_MONITORING_CONFIG_NAME, "machine_monitoring")
        return os.path.join(env_basic.config_dir, config_dir_relative)

    @property
    def machine_monitoring_error_logfile(self) -> str:
        """ .. envvar:: FASTIOT_MACHINE_MONITORING_ERROR_LOGFILE
        """
        return os.getenv(FASTIOT_MACHINE_MONITORING_ERROR_LOGFILE, "/var/fastiot/logs/error.log")


env_opcua = OPCUAEnv()
