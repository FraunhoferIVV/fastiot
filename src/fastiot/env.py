import os


FASTIOT_BROKER_HOST = 'FASTIOT_BROKER_HOST'
FASTIOT_BROKER_PORT = 'FASTIOT_BROKER_PORT'
FASTIOT_BROKER_DEFAULT_TIMEOUT = 'FASTIOT_BROKER_DEFAULT_TIMEOUT'
FASTIOT_BROKER_STREAM_TIMEOUT = 'FASTIOT_BROKER_STREAM_TIMEOUT'


class BrokerEnv:
    @property
    def host(self) -> str:
        return os.environ[FASTIOT_BROKER_HOST]

    @property
    def port(self) -> int:
        return int(os.getenv(FASTIOT_BROKER_PORT, 4222))

    @property
    def default_timeout(self) -> float:
        return float(os.getenv(FASTIOT_BROKER_DEFAULT_TIMEOUT, 30))

    @property
    def stream_timeout(self) -> float:
        return float(os.getenv(FASTIOT_BROKER_STREAM_TIMEOUT, 10))


fastiot_broker_env = BrokerEnv()
