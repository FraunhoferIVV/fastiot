""" Helpers to make writing tests easier """
import os
import subprocess
import sys
import time
from asyncio.subprocess import Process
from typing import Optional

from fastiot.cli.constants import CONFIGURE_FILE_NAME
from fastiot.cli.model.project import ProjectContext
from fastiot.env.env import env_tests


def populate_test_env(deployment_name: Optional[str] ="") :
    """
    Populates the local environment with test env vars from the test integration deployment.

    It will import the .env-file from build dir and raise an error if not available. It will then overwrite these values
    from the .env-file within deployment dir for more robustness because sometimes the developer forgets to rebuild the
    config. Overwriting the env values with the deployment dir should solve it.

    :param deployment_name: Optionally specify a different deployment to be used instead of the integration test
    """

    if not os.path.isfile(os.path.join(os.getcwd(), CONFIGURE_FILE_NAME)):
        _set_cwd_project_root_dir()

    context = ProjectContext.default
    context.project_root_dir = os.getcwd()

    deployment_name = deployment_name or context.integration_test_deployment

    deployment_dir = context.deployment_dir(deployment_name)
    if os.path.exists(deployment_dir) is False:
        raise RuntimeError(f"Expected deployment '{deployment_name}' to be configured. "
                           "Please configure it via `fiot config`")

    env = context.build_env_for_deployment(deployment_name)
    if env_tests.use_internal_hostnames:
        env = {**env, **context.build_env_for_internal_services_deployment(deployment_name)}

    env = {**env, **context.env_for_deployment(deployment_name)}

    for key, value in env.items():
        os.environ[key] = value

def _set_cwd_project_root_dir():
    from fastiot import logging

    while len(os.getcwd()) >= 3:  # Stop when reaching something like / or C:\
        os.chdir('..')
        if os.path.isfile(os.path.join(os.getcwd(), CONFIGURE_FILE_NAME)):
            return

    logging.error("Could not find file %s in current path. Please set start path to project root dir!")
    sys.exit(1)


class BackgroundProcess:
    """
    Class to help with FastIoT Services as background process for tests using a separate python process.

    This may help if your service already has many internal tasks and needs to act as a server for your unit or
    integration tests.
    Make sure to have a reasonable long startup time for the service to start. If in doubt use a couple seconds and
    slowly reduce when testing locally.


    >>> from fastiot_sample_services.producer.producer_module import ExampleProducerService
    >>> from fastiot.testlib import BackgroundProcess
    >>>
    >>> with BackgroundProcess(ExampleProducerService, startup_time=1.5):
    >>>     pass  # Do some stuff with the service
    >>> # Outside the context the service will be terminated and killed
    """

    def __init__(self, service: object, startup_time: float = 0.2, stop_time: float = 0.05):
        """
        Constructor

        :param service: The Service inheriting from :class:`fastiot.core.service.FastIoTService` (without ())
        :param startup_time: The time to wait for the service to become ready, defaults to 0.2 seconds
        """
        self.service = service
        self.process: Optional[Process] = None
        self.startup_time = startup_time
        self.stop_time = stop_time

    def __enter__(self):
        class_name = ".".join(self.service.__module__.split('.')[0:-1]) + ".run"
        proc = [sys.executable, "-m", class_name]
        self.process = subprocess.Popen(proc)
        time.sleep(self.startup_time)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.process.terminate()
        time.sleep(self.stop_time)
