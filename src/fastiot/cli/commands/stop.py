""" Implements some stop commands for e.g. environments. """
import logging
import os
import subprocess
from typing import Optional, List
from fastiot.cli.model.project import ProjectContext

import typer

from fastiot.cli.commands.deploy import _deployment_completion
from fastiot.cli.constants import DEPLOYMENTS_CONFIG_DIR
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
         use_test_deployment: Optional[bool] = typer.Option(False, help="Explicitly set the environment to the "
                                                                        "test environment specified in the project. "
                                                                        "Useful for the CI runner")
         ):
    """
    Stops the selected environment.
    """
    context = ProjectContext.default

    if use_test_deployment:
        deployment_name = context.integration_test_deployment
        if not deployment_name:
            logging.warning("No `integration_test_deployment` configured. Exiting.")
            raise typer.Exit(0)

    if deployment_name is None:
        logging.error("You have to define an environment to stop or use the optional argument --use-test-deployment!")
        raise typer.Exit(1)

    cwd = os.path.join(context.project_root_dir, context.build_dir, DEPLOYMENTS_CONFIG_DIR,
                       deployment_name)

    cmd = "docker-compose "

    project_name = project_name or context.project_namespace + "_" + deployment_name
    cmd += "--project-name=" + project_name

    if service_names is not None and len(service_names) > 0:
        cmd += " rm --stop --force " + " ".join(service_names)
    else:
        cmd += " down"
    if use_test_deployment or deployment_name == context.integration_test_deployment:
        cmd += " --volumes"  # Remove test volumes right away

    logging.debug("Running command to stop the environment: %s in path %s", cmd, cwd)
    env = os.environ.copy()
    env['COMPOSE_HTTP_TIMEOUT'] = '300'
    exit_code = subprocess.call(f"{cmd}".split(), cwd=cwd, env=env)
    if exit_code != 0:
        logging.error("Stopping the environment failed with exit code %s", str(exit_code))
        raise typer.Exit(exit_code)
