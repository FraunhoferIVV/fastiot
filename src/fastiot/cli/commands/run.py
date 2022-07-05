import logging
import os
import subprocess
import sys
from typing import Optional, List

import typer

from fastiot.cli.constants import DEPLOYMENTS_CONFIG_DIR
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import run_cmd, DEFAULT_CONTEXT_SETTINGS


def _deployment_completion() -> List[str]:
    return get_default_context().project_config.deployment_names


@run_cmd.command(context_settings=DEFAULT_CONTEXT_SETTINGS)
def deployment(deployment_name: Optional[str] = typer.Argument(default=None, shell_complete=_deployment_completion,
                                                               help="Select the environment to start."),
               service_names: Optional[List[str]] = typer.Argument(default=None,
                                                                    help="Optionally specify services to be started "
                                                                         "from the environment."),
               detach: Optional[bool] = typer.Option(False, "-d", "--detach", help="Use to run this task in the "
                                                                                    "background (detached)"),
               project_name: Optional[str] = typer.Option(None, help="Manually set project name for docker-compose"),
               run_test_deployment: Optional[bool] = typer.Option(False, help="Explicitly set the environment to the "
                                                                        "test environment specified in the project. "
                                                                        "Useful for the CI runner")
               ):
    """ Starts up the selected environment.
    Be aware, that the configuration needs to be built manually before using `fastiot.cli configure`."""
    project_config = get_default_context().project_config

    if run_test_deployment:
        deployment_name = project_config.integration_test_deployment

    if deployment_name is None:
        logging.error("You have to define an environment to start or use the optional --run-test-deployment!")
        sys.exit(-1)

    cmd = ["docker-compose"]
    project_name = project_name or project_config.project_namespace + "__" + deployment_name
    cmd.append("--project-name=" + project_name)

    cmd.append("up")
    if detach:
        cmd.append("-d")

    if service_names is not None:
        cmd += service_names

    cwd = os.path.join(project_config.project_root_dir, project_config.build_dir, DEPLOYMENTS_CONFIG_DIR,
                       deployment_name)
    logging.debug("Running command to start the environment: %s", " ".join(cmd))
    os.environ['COMPOSE_HTTP_TIMEOUT'] = '300'
    exit_code = subprocess.call(cmd, cwd=cwd)
    if exit_code != 0:
        logging.error("Running the environment failed with exit code %s", str(exit_code))
        sys.exit(exit_code)


@run_cmd.command(name='tests')
def run_unittests():
    """
    This command will trigger all unittests found in the configured test package. Be aware that this will not
    automatically start your integration test deployment with e.g. a message broker. You may start this using the
    command ``fastiot.cli run deployment --run-test-deployment`` (:func:`fastiot.cli.commands.run.deployment`)
    """
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'  # Stop writing an __pycache__ for clean containers afterwards

    project_config = get_default_context().project_config

    if project_config.test_package is None:
        logging.info("No test_package defined in configure.py. Skipping unittests.")
        sys.exit(0)

    env = os.environ.copy()
    src_dir = os.path.join(project_config.project_root_dir, 'src')
    env['PYTHONPATH'] = src_dir

    cmd = sys.executable + f" -m pytest --rootdir={src_dir} --junitxml=pytest_report.xml " \
                           f"--cov={src_dir} --cov-report=xml --cov-branch -p no:cacheprovider"

    exit_code = subprocess.call(cmd.split(),
                                cwd=project_config.project_root_dir,
                                env=env)
    if exit_code != 0:
        logging.error("Running unittests failed with exit code %s", str(exit_code))
        sys.exit(exit_code)
