""" Helpers to make writing tests easier """
import os
from fastiot.cli.model.project import ProjectContext

from fastiot.env.env import env_tests


def populate_test_env():
    """Populates the local environment with test env vars from the test integration deployment. """
    context = ProjectContext.default

    if os.path.exists(context.deployment_build_dir(context.integration_test_deployment)) is False:
        raise RuntimeError(f"Expected test deployment '{context.integration_test_deployment}' to be configured. Please configure it via `fiot config`")

    env = context.build_env_for_deployment(context.integration_test_deployment)
    if env_tests.use_internal_hostnames:
        env = {**env, **context.build_env_for_internal_services_deployment(context.integration_test_deployment)}

    for key, value in env.items():
        os.environ[key] = value

