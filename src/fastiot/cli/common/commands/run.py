import logging
import os
import subprocess
import sys
from typing import Optional, List

import typer

from fastiot.cli.constants import GENERATED_DEPLOYMENTS_DIR
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import run_cmd, DEFAULT_CONTEXT_SETTINGS


def _environment_completion() -> List[str]:
    return get_default_context().project_config.get_all_deployment_names()


@run_cmd.command(context_settings=DEFAULT_CONTEXT_SETTINGS)
def environment(environment_name: Optional[str] = typer.Argument(default=None, autocompletion=_environment_completion,
                                                                 help="Select the environment to start."),
                service_names: Optional[List[str]] = typer.Argument(default=None,
                                                                    help="Optionally specify services to be started "
                                                                         "from the environment."),
                detach: Optional[bool] = typer.Option(False, "-d", "--detach", help="Use to run this task in the "
                                                                                    "background (detached)"),
                project_name: Optional[str] = typer.Option(None, help="Manually set project name for docker-compose")):
    """ Starts up the selected environment.
    Be aware, that the configuration needs to be built manually before using `fastiot.cli configure`."""
    project_config = get_default_context().project_config

    cmd = ["docker-compose"]
    project_name = project_name or project_config.project_namespace + "__" + environment_name
    cmd.append("--project-name=" + project_name)

    cmd.append("up")
    if detach:
        cmd.append("-d")

    if service_names is not None:
            cmd += service_names

    cwd = os.path.join(project_config.project_root_dir, GENERATED_DEPLOYMENTS_DIR,
                       environment_name)
    logging.debug("Running command to start the environment: %s", " ".join(cmd))
    os.environ['COMPOSE_HTTP_TIMEOUT'] = '300'
    exit_code = subprocess.call(cmd, cwd=cwd)
    if exit_code != 0:
        logging.error("Running the environment failed with exit code %s", str(exit_code))
        sys.exit(exit_code)
