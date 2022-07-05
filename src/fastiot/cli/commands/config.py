import os
from typing import Optional, List

import typer

from fastiot.cli.commands.run import _deployment_completion
from fastiot.cli.constants import FASTIOT_DEFAULT_TAG, FASTIOT_DOCKER_REGISTRY, \
    FASTIOT_NET, FASTIOT_NO_PORT_MOUNTS, DEPLOYMENTS_CONFIG_DIR
from fastiot.cli.helper_fn import get_jinja_env
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import app, DEFAULT_CONTEXT_SETTINGS


@app.command(context_settings=DEFAULT_CONTEXT_SETTINGS)
def config(deployments: Optional[List[str]] = typer.Argument(default=None, shell_complete=_deployment_completion,
                                                             help="The deployment configs to generate. Default: all "
                                                                  "configs"),
           tag: str = typer.Option('latest', '-t', '--tag',
                                   help="Specify a default tag for the deployment(s).",
                                   envvar=FASTIOT_DEFAULT_TAG),
           docker_registry: str = typer.Option('', '-r', '--docker-registry',
                                               help="Specify a default docker registry for the deployment(s)",
                                               envvar=FASTIOT_DOCKER_REGISTRY),
           net: str = typer.Option("fastiot-net", '-n', '--net',
                                   help="The name of the network for all services.",
                                   envvar=FASTIOT_NET),
           pull_always: bool = typer.Option(False, '--pull-always',
                                            help="If given, it will always use 'docker pull' command to pull images "
                                                 "from specified docker registries before reading manifest.yaml "
                                                 "files."),
           no_port_mounts: bool = typer.Option(False, '--no-port-mounts',
                                               help="If true, it will skip mounts for infrastructure services.",
                                               envvar=FASTIOT_NO_PORT_MOUNTS),
           no_env_var_overrides: bool = typer.Option(False, '--no-env-var',
                                                     help="Per default, it will override environment variables for "
                                                          "services with current process environment variables. "
                                                          "Using this flag this behavior can be disabled. Environment "
                                                          "variables configured on modules level will never be "
                                                          "overridden.")):
    """
    This command generates deployment configs. Per default, it generates all configs. Optionally, you can specify a
    config to only generate a single deployment config. All generated files will be placed inside the build dir of your
    project.

    For each service the docker images will be executed to import the manifest.yaml file. Therefore, if you want to
    build one or more deployments you have to be logged in and connected to the corresponding docker registries or build
    the images locally.
    """

    project_config = get_default_context().project_config

    if deployments:
        deployment_names = []
        for deployment in deployment_names:
            if deployment not in project_config.deployment_names:
                raise ValueError(f"Deployment '{deployment}' is not in project specified.")
            if deployment not in deployment_names:
                deployment_names.append(deployment)
    else:
        deployment_names = project_config.deployment_names

    for deployment_name in deployment_names:
        deployment_dir = os.path.join(project_config.project_root_dir, project_config.build_dir, DEPLOYMENTS_CONFIG_DIR,
                                      deployment_name)
        try:
            os.makedirs(deployment_dir)
        except FileExistsError:
            pass  # No need to create directory twice

        with open(os.path.join(deployment_dir, 'docker-compose.yaml'), "w") as docker_compose_file:
            docker_compose_template = get_jinja_env().get_template('docker-compose.yaml.jinja')
            docker_compose_file.write(docker_compose_template.render(docker_net_name=net))
