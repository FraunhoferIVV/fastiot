import os


FASTIOT_BROKER_HOST = 'FASTIOT_BROKER_HOST'
FASTIOT_BROKER_PORT = 'FASTIOT_BROKER_PORT'
FASTIOT_BROKER_DEFAULT_TIMEOUT = 'FASTIOT_BROKER_DEFAULT_TIMEOUT'


class BrokerEnv:
    @property
    def host(self) -> str:
        return os.environ[FASTIOT_BROKER_HOST]

    @property
    def port(self) -> str:
        return os.environ[FASTIOT_BROKER_PORT]

    @property
    def default_timeout(self) -> float:
        return float(os.getenv(FASTIOT_BROKER_DEFAULT_TIMEOUT, 30))


fastiot_broker_env = BrokerEnv()
