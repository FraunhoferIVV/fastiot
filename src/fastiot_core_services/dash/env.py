import os

FASTIOT_HOST_PORT = 'FASTIOT_HOST_PORT'
FASTIOT_DASH_PORT = 'FASTIOT_DASH_PORT'


class DashModuleConstants:

    @property
    def dash_host(self) -> str:
        return str(os.environ.get(FASTIOT_HOST_PORT, 'localhost'))

    @property
    def dash_port(self) -> int:
        return int(os.environ.get(FASTIOT_DASH_PORT, 5802))


env_dash = DashModuleConstants()
