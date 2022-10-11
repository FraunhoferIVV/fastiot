import os


FASTIOT_SAMPLE_DASH_PORT = 'FASTIOT_SAMPLE_DASH_PORT'


class DashModuleConstants:

    @property
    def dash_port(self) -> int:
        return int(os.environ.get(FASTIOT_SAMPLE_DASH_PORT, 5801))


env_dash = DashModuleConstants()
