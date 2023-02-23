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
FASTIOT_OPC_UA_CONFIG_NAME = 'FASTIOT_OPC_UA_CONFIG_NAME'
FASTIOT_OPC_UA_ERROR_LOGFILE = 'FASTIOT_OPC_UA_ERROR_LOGFILE'


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

        The Endpoint Url to the OPC-UA Server, e.g. "opc.tcp://127.0.0.1:5000"
        """
        return os.environ[FASTIOT_OPCUA_ENDPOINT_URL]

    @property
    def security_string(self) -> str:
        """ .. envvar:: FASTIOT_OPCUA_SECURITY_STRING

        A security string if its needed, e.g.
        "Basic256Sha256,Sign,/path/to/certificate/test_certificate.der,/path/to/key/test_key.pem"

        It is recommended to place needed certificates inside a config dir and locate it there.
        """
        return os.getenv(FASTIOT_OPCUA_SECURITY_STRING, '')

    @property
    def user(self) -> str:
        """ .. envvar:: FASTIOT_OPCUA_USER

        Username for the OPC UA connection.
        """
        return os.getenv(FASTIOT_OPCUA_USER, '')

    @property
    def password(self) -> str:
        """ .. envvar:: FASTIOT_OPCUA_PASSWORD

        Password for the OPC UA Connection.
        """
        return os.getenv(FASTIOT_OPCUA_PASSWORD, '')

    @property
    def application_uri(self) -> str:
        """ .. envvar:: FASTIOT_OPCUA_APPLICATION_URI

        In rare cases it is needed to specify an application uri to connect to an OPC-UA Server which can be set with
        this env variable, e.g. "urn:freeopcua:client"
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

        Can be one of 'polling' (default), 'polling_always' or 'subscription'.

        Polling mode requests all OPC-UA nodes in a loop. You can specify the loop delay via
        'FASTIOT_OPCUA_POLLING_DELAY'. If you use 'polling_always', it will publish a value for each value retrieved.
        Running in 'polling' will only publish all values in the first run and in consecutive loop runs it will only
        publish value changes.

        If using subscriptions mode, it will utilize OPC-UA Subscriptions to publish retrieved value changes; depending
        on the OPC-UA Server implementation. This can be useful when working with many OPC-UA nodes where polling takes
        too long to complete.
        Please note that Subscriptions are an optional OPC-UA feature and not all Servers might support it nor might
        provide a stable implementation. It is recommended when using subscriptions, to also use
        'FASTIOT_OPCUA_MAX_ALLOWED_DATA_DELAY' to handle connection errors.

        Generally speaking, polling is useful for a small number of nodes <10 and subscriptions for many nodes >1000
        depending on the usecase. (There is no general answer what is better for values between 10 and 1000.)
        """
        return OPCUARetrievalMode(os.getenv(FASTIOT_OPCUA_RETRIEVAL_MODE, OPCUARetrievalMode.polling))

    @property
    def opc_ua_reader_config_dir(self) -> str:
        """ .. envvar:: FASTIOT_OPC_UA_CONFIG_NAME

        Specify a config name. This can be useful when running multiple instances of machine monitoring with a different
        opc-ua node configuration inside the config_dir. Defaults to "opc_ua_reader" and is relative to the config
        dir.
        """
        config_dir_relative = os.getenv(FASTIOT_OPC_UA_CONFIG_NAME, "opc_ua_reader")
        return os.path.join(env_basic.config_dir, config_dir_relative)

    @property
    def opc_ua_reader_error_logfile(self) -> str:
        """ .. envvar:: FASTIOT_OPC_UA_ERROR_LOGFILE

        Specify an error log file. In this error log file are connection errors logged. If there is any error logged,
        the machine monitor is marked as unhealthy and depending on the deployment is restarted.

        This can be useful if the OPC-UA Server has unstable subscriptions - so when they break the service is
        restarted.
        """
        return os.getenv(FASTIOT_OPC_UA_ERROR_LOGFILE, "/var/fastiot/logs/error.log")


env_opcua = OPCUAEnv()
