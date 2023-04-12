import os

FASTIOT_IS_CI_RUNNER = 'FASTIOT_IS_CI_RUNNER'
FASTIOT_WITHIN_CONTAINER = 'FASTIOT_WITHIN_CONTAINER'


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
        .. envvar:: FASTIOT_IS_CI_RUNNER

        Set to true to enable some CI-runner specific features like keeping the buildkit container running.
        """
        return os.environ.get(FASTIOT_WITHIN_CONTAINER, 'False').lower().startswith('t')


env_cli = CLIConstants()
