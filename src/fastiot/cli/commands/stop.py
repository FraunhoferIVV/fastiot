""" Implements some stop commands for e.g. environments. """
import logging
import os
import subprocess
import sys
from typing import Optional, List

import typer

from fastiot.cli.commands.deploy import _deployment_completion
from fastiot.cli.constants import DEPLOYMENTS_CONFIG_DIR
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import DEFAULT_CONTEXT_SETTINGS, app


@app.command(context_settings=DEFAULT_CONTEXT_SETTINGS)
def stop(deployment_name: Optional[str] = typer.Argument(default=None, shell_complete=_deployment_completion,
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
    Stops the selected environment.
    """
    project_config = get_default_context().project_config

    if stop_test_deployment:
        deployment_name = project_config.integration_test_deployment
        if not deployment_name:
            logging.warning("No `integration_test_deployment` configured. Exiting.")
            raise typer.Exit(0)

    if deployment_name is None:
        logging.error("You have to define an environment to start or use the optional --run-test-deployment!")
        raise typer.Exit(1)

    cwd = os.path.join(project_config.project_root_dir, project_config.build_dir, DEPLOYMENTS_CONFIG_DIR,
                       deployment_name)

    cmd = "docker-compose "

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
