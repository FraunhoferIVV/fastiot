import os


FASTIOT_SAMPLE_FASTIOT_PORT = 'FASTIOT_SAMPLE_FASTIOT_PORT'


class FastAPIModuleConstants:

    @property
    def fastapi_port(self) -> int:
        """ ..envvar:: FASTIOT_SAMPLE_FASTIOT_PORT

        Set the port for the FastAPI REST interface in the FastAPI sample module.
        """
        return int(os.environ.get(FASTIOT_SAMPLE_FASTIOT_PORT, "5800"))


env_fastapi = FastAPIModuleConstants()
