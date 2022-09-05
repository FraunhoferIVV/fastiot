import logging
import os
import subprocess
import sys
from typing import Optional, List

import typer

from fastiot.cli.constants import DEPLOYMENTS_CONFIG_DIR
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import app, DEFAULT_CONTEXT_SETTINGS


def _deployment_completion() -> List[str]:
    return get_default_context().project_config.deployment_names


@app.command(context_settings=DEFAULT_CONTEXT_SETTINGS)
def start(deployment_name: Optional[str] = typer.Argument(default=None, shell_complete=_deployment_completion,
                                                          help="Select the environment to start."),
          service_names: Optional[List[str]] = typer.Argument(default=None,
                                                              help="Optionally specify services to be started "
                                                                   "from the environment."),
          detach: Optional[bool] = typer.Option(False, "-d", "--detach",
                                                help="Use to run this task in the background (detached)"),
          project_name: Optional[str] = typer.Option(None, help="Manually set project name for docker-compose"),
          use_test_deployment: Optional[bool] = typer.Option(False,
                                                             help="Explicitly set the deployment_name to specified "
                                                                  "integration test deployment. Useful for the CI "
                                                                  "runner")
          ):
    """ Starts the selected environment.
    Be aware that the configuration needs to be built manually before using `fiot config`."""
    project_config = get_default_context().project_config

    if use_test_deployment:
        deployment_name = project_config.integration_test_deployment
        if not deployment_name:
            logging.warning("You have not configured any integration_test_deployment in your configure.py. Exiting.")
            raise typer.Exit(0)

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
    exit_code = 0
    try:
        exit_code = subprocess.call(cmd, cwd=cwd)
    except KeyboardInterrupt:
        if not detach:
            from fastiot.cli.commands.stop import deployment as stop_deployment
            stop_deployment(deployment_name=deployment_name,
                            service_names=service_names,
                            project_name=project_name,
                            stop_test_deployment=run_test_deployment)
    if exit_code != 0:
        logging.error("Running the environment failed with exit code %s", str(exit_code))
        sys.exit(exit_code)


