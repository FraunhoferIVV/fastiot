import getpass
import logging
import os
import subprocess
from typing import Optional, List

import typer

from fastiot.cli.commands.stop import stop
from fastiot.cli.constants import DEPLOYMENTS_CONFIG_DIR, FASTIOT_PULL_ALWAYS
from fastiot.cli.model.project import ProjectContext
from fastiot.cli.typer_app import app, DEFAULT_CONTEXT_SETTINGS


def _deployment_completion() -> List[str]:
    return ProjectContext.default.deployment_names


@app.command(context_settings=DEFAULT_CONTEXT_SETTINGS)
def start(deployment_name: Optional[str] = typer.Argument(default=None, shell_complete=_deployment_completion,
                                                          help="Select the environment to start."),
          service_names: Optional[List[str]] = typer.Argument(default=None,
                                                              help="Optionally specify services to be started "
                                                                   "from the environment."),
          detach: bool = typer.Option(False, "-d", "--detach",
                                      help="Use to run this task in the background (detached)"),
          project_name: str = typer.Option('', help="Manually set project name for docker-compose"),
          use_test_deployment: Optional[bool] = typer.Option(False,
                                                             help="Explicitly set the deployment_name to specified "
                                                                  "integration test deployment. Useful for the CI "
                                                                  "runner"),
          pull_always: bool = typer.Option(False, '--pull-always',
                                           help="If given, it will always use 'docker pull' command to pull images "
                                                "from specified docker registries before starting the services. ",
                                           envvar=FASTIOT_PULL_ALWAYS),
          ):
    """ Starts the selected environment.
    Be aware that the configuration needs to be built manually before using `fiot config`."""
    context = ProjectContext.default

    if use_test_deployment:
        deployment_name = context.integration_test_deployment
        if not deployment_name:
            logging.warning("You have not configured any integration_test_deployment in your configure.py. Exiting.")
            raise typer.Exit(0)

    if deployment_name is None:
        logging.error("You have to define an environment to start or use the optional --use-test-deployment!")
        raise typer.Exit(-1)

    cwd = os.path.join(context.project_root_dir, context.build_dir, DEPLOYMENTS_CONFIG_DIR,
                       deployment_name)

    cmd = ["docker-compose"]
    project_name = project_name or getpass.getuser() + "__" + context.project_namespace + "__" + deployment_name
    cmd.append("--project-name=" + project_name)

    if pull_always:
        pull_cmd = cmd + ["pull"]
        exit_code = subprocess.call(pull_cmd, cwd=cwd)
        if exit_code != 0:
            logging.warning("Pulling images was not successful. Trying to continue.")

    cmd.append("up")
    if detach:
        cmd.append("-d")

    if service_names is not None:
        cmd += service_names

    logging.debug("Running command to start the environment: %s", " ".join(cmd))
    os.environ['COMPOSE_HTTP_TIMEOUT'] = '300'
    exit_code = 0
    try:
        exit_code = subprocess.call(cmd, cwd=cwd)
    except KeyboardInterrupt:
        if not detach:
            stop(deployment_name=deployment_name,
                 service_names=service_names,
                 project_name=project_name,
                 use_test_deployment=use_test_deployment)
    if exit_code != 0:
        logging.error("Running the environment failed with exit code %s", str(exit_code))
        raise typer.Exit(exit_code)
