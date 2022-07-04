import os
from typing import Optional

import typer

from fastiot.cli.commands.run import _deployment_completion
from fastiot.cli.constants import GENERATED_DEPLOYMENTS_DIR
from fastiot.cli.helper_fn import get_jinja_env
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import app


@app.command()
def config(deployment_name: Optional[str] = typer.Argument(default=None, shell_complete=_deployment_completion,
                                                           help="Select the environment to start."),
           tag: Optional[str] = typer.Option("latest"),
           docker_net_name: Optional[str] = typer.Option("fastiot_net"),
           mount_service_ports: Optional[bool] = typer.Option(False),
           test_deployment_only: Optional[bool] = typer.Option(False,
                                                               help="Create only configuration defined in the test "
                                                             "environment. This is especially useful in the CI-runner"),
           ):
    """ TODO: This implements only the very basics to get the build pipeline started. Actual implementation needed. """

    project_config = get_default_context().project_config

    if test_deployment_only:
        deployment_names = [project_config.test_config]
    elif deployment_name is None:
        deployment_names = project_config.get_all_deployment_names()
    else:
        deployment_names = [deployment_name]

    for deployment_name in deployment_names:
        deployment_dir = os.path.join(project_config.project_root_dir, GENERATED_DEPLOYMENTS_DIR, deployment_name)
        try:
            os.makedirs(deployment_dir)
        except FileExistsError:
            pass  # No need to create directory twice

        with open(os.path.join(deployment_dir, 'docker-compose.yaml'), "w") as docker_compose_file:
            docker_compose_template = get_jinja_env().get_template('docker-compose.yaml.jinja')
            docker_compose_file.write(docker_compose_template.render(docker_net_name=docker_net_name))
