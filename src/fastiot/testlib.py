""" Helpers to make writing tests easier """
import os
import sys

from fastiot import logging
from fastiot.cli.constants import CONFIGURE_FILE_NAME
from fastiot.cli.model.project import ProjectContext

from fastiot.env.env import env_tests


def populate_test_env():
    """Populates the local environment with test env vars from the test integration deployment. """

    if not os.path.isfile(os.path.join(os.getcwd(), CONFIGURE_FILE_NAME)):
        _set_cwd_project_root_dir()

    context = ProjectContext.default
    context.project_root_dir = os.getcwd()

    if os.path.exists(context.deployment_build_dir(context.integration_test_deployment)) is False:
        raise RuntimeError(f"Expected test deployment '{context.integration_test_deployment}' to be configured. "
                           "Please configure it via `fiot config`")

    env = context.build_env_for_deployment(context.integration_test_deployment)
    if env_tests.use_internal_hostnames:
        env = {**env, **context.build_env_for_internal_services_deployment(context.integration_test_deployment)}

    for key, value in env.items():
        os.environ[key] = value

def _set_cwd_project_root_dir():
    while len(os.getcwd()) >= 3:  # Stop when reaching something like / or C:\
        os.chdir('..')
        if os.path.isfile(os.path.join(os.getcwd(), CONFIGURE_FILE_NAME)):
            return

    logging.error("Could not find file %s in current path. Please set start path to project root dir!")
    sys.exit(1)
