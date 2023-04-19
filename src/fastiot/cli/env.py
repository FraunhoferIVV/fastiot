import os

FASTIOT_IS_CI_RUNNER = 'FASTIOT_IS_CI_RUNNER'
FASTIOT_WITHIN_CONTAINER = 'FASTIOT_WITHIN_CONTAINER'
FASTIOT_USE_DEPLOYMENT = 'FASTIOT_USE_DEPLOYMENT'


class CLIConstants:
    """ Some environment variables for the CI runner used internally and not available as command line option. """

    @property
    def is_ci_runner(self) -> bool:
        """
        .. envvar:: FASTIOT_IS_CI_RUNNER

        Set to true to enable some CI-runner specific features like keeping the buildkit container running.
        """
        return os.environ.get(FASTIOT_IS_CI_RUNNER, 'False').lower().startswith('t')

    @property
    def within_container(self) -> bool:
        """
        .. envvar:: FASTIOT_WITHIN_CONTAINER

        Set to true to enable some CI-runner specific features like keeping the buildkit container running.
        """
        return os.environ.get(FASTIOT_WITHIN_CONTAINER, 'False').lower().startswith('t')

    @property
    def use_local_deployment(self) -> str:
        """
        .. envvar:: FASTIOT_USE_DEPLOYMENT

        Set this variable in your IDE when running services locally to overwrite the integration test deployment used
        per default.
        """
        return os.environ.get(FASTIOT_USE_DEPLOYMENT, "")


env_cli = CLIConstants()
