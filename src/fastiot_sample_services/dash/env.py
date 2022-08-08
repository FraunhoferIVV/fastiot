import os


EXAMPLE_SAM_DASH_PORT = 'EXAMPLE_SAM_DASH_PORT'


class DashModuleConstants:

    @property
    def dash_port(self) -> int:
        return int(os.environ.get(EXAMPLE_SAM_DASH_PORT, 5801))


env_dash = DashModuleConstants()
