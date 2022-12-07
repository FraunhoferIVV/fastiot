""" Helpers to make writing tests easier """
import os
import sys

from fastiot import logging
from fastiot.cli.constants import CONFIGURE_FILE_NAME
from fastiot.cli.model.project import ProjectContext

from fastiot.env.env import env_tests


def populate_test_env():
    """
    Populates the local environment with test env vars from the test integration deployment.

    It will import the .env-file from build dir and raise an error if not available. It will then overwrite these values
    from the .env-file within deployment dir for more robustness because sometimes the developer forgets to rebuild the
    config. Overwriting the env values with the deployment dir should solve it.
    """

    if not os.path.isfile(os.path.join(os.getcwd(), CONFIGURE_FILE_NAME)):
        _set_cwd_project_root_dir()

    context = ProjectContext.default
    context.project_root_dir = os.getcwd()
    deployment_dir = context.deployment_dir(context.integration_test_deployment)
    if os.path.exists(deployment_dir) is False:
        raise RuntimeError(f"Expected test deployment '{context.integration_test_deployment}' to be configured. "
                           "Please configure it via `fiot config`")

    env = context.build_env_for_deployment(context.integration_test_deployment)
    if env_tests.use_internal_hostnames:
        env = {**env, **context.build_env_for_internal_services_deployment(context.integration_test_deployment)}

    env = {**env, **context.env_for_deployment(context.integration_test_deployment)}

    for key, value in env.items():
        os.environ[key] = value

def _set_cwd_project_root_dir():
    while len(os.getcwd()) >= 3:  # Stop when reaching something like / or C:\
        os.chdir('..')
        if os.path.isfile(os.path.join(os.getcwd(), CONFIGURE_FILE_NAME)):
            return

    logging.error("Could not find file %s in current path. Please set start path to project root dir!")
    sys.exit(1)
