""" Implements some stop commands for e.g. environments. """
import logging
import os
import subprocess
import sys
from typing import Optional, List

import typer

from fastiot.cli.commands.run import _deployment_completion
from fastiot.cli.constants import GENERATED_DEPLOYMENTS_DIR
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import DEFAULT_CONTEXT_SETTINGS, stop_cmd


@stop_cmd.command(context_settings=DEFAULT_CONTEXT_SETTINGS)
def deployment(deployment_name: Optional[str] = typer.Argument(default=None, shell_complete=_deployment_completion,
                                                               help="Select the environment to stop."),
               service_names: Optional[List[str]] = typer.Argument(default=None,
                                                                    help="Optionally specify services to be stopped "
                                                                         "from the environment. This will only stop "
                                                                         "the services but not remove the containers."
                                                                         "(docker-compose stop instead of down)"),
               project_name: Optional[str] = typer.Option(None, help="Manually set project name for docker-compose"),
               stop_test_deployment: Optional[bool] = typer.Option(False, help="Explicitly set the environment to the "
                                                                         "test environment specified in the project. "
                                                                         "Useful for the CI runner")
               ):
    """
    Stops up the selected environment.
    """
    project_config = get_default_context().project_config

    if stop_test_deployment:
        deployment_name = project_config.test_config

    if deployment_name is None:
        logging.error("You have to define an environment to start or use the optional --run-test-deployment!")
        sys.exit(-1)

    cwd = os.path.join(project_config.project_root_dir, GENERATED_DEPLOYMENTS_DIR,
                       deployment_name)

    cmd = f"docker-compose "

    project_name = project_name or project_config.project_namespace + "__" + deployment_name
    cmd += "--project-name=" + project_name

    if service_names is not None and len(service_names) > 0:
        cmd += " stop " + " ".join(service_names)
    else:
        cmd += " down"
    if stop_test_deployment:
        cmd += " --volumes"  # Remove test volumes right away

    logging.debug("Running command to stop the environment: %s in path %s", cmd, cwd)
    env = os.environ.copy()
    env['COMPOSE_HTTP_TIMEOUT'] = '300'
    exit_code = subprocess.call(f"{cmd}".split(), cwd=cwd, env=env)
    if exit_code != 0:
        logging.error("Stopping the environment failed with exit code %s", str(exit_code))
        sys.exit(exit_code)
    if service_names is not None and len(service_names) > 0:
        cmd = "docker-compose rm -f " + " ".join(service_names)
        exit_code = subprocess.call(cmd.split(), cwd=cwd)
        if exit_code != 0:
            logging.error("Stopping the environment failed with exit code %s", str(exit_code))
            sys.exit(exit_code)
