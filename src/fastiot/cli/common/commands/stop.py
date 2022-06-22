""" Implements some stop commands for e.g. environments. """
import logging
import os
import subprocess
import sys
from typing import Optional, List

import typer

from fastiot.cli.common.commands.run import _environment_completion
from fastiot.cli.constants import GENERATED_DEPLOYMENTS_DIR
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import DEFAULT_CONTEXT_SETTINGS, stop_cmd


@stop_cmd.command(context_settings=DEFAULT_CONTEXT_SETTINGS)
def environment(environment_name: Optional[str] = typer.Argument(default=None, autocompletion=_environment_completion,
                                                                 help="Select the environment to stop."),
                service_names: Optional[List[str]] = typer.Argument(default=None,
                                                                    help="Optionally specify services to be stopped "
                                                                         "from the environment. This will only stop "
                                                                         "the services but not remove the containers."
                                                                         "(docker-compose stop instead of down)")
                ):
    """
    Stops up the selected environment.
    """
    project_config = get_default_context().project_config

    cmd = "docker-compose "

    if service_names is not None and len(service_names) > 0:
        cmd += "stop " + " ".join(service_names)
    else:
        cmd += "down"

    cwd = os.path.join(project_config.project_root_dir, GENERATED_DEPLOYMENTS_DIR,
                       environment_name)
    logging.debug("Running command to stop the environment: %s", cmd)
    os.environ['COMPOSE_HTTP_TIMEOUT'] = '300'
    exit_code = subprocess.call(f"{cmd}".split(), cwd=cwd)
    if exit_code != 0:
        logging.error("Stopping the environment failed with exit code %s", str(exit_code))
        sys.exit(exit_code)
    if service_names is not None and len(service_names) > 0:
        cmd = "docker-compose rm -f " + " ".join(service_names)
        exit_code = subprocess.call(cmd.split(), cwd=cwd)
        if exit_code != 0:
            logging.error("Stopping the environment failed with exit code %s", str(exit_code))
            sys.exit(exit_code)
