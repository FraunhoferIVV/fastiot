import os
from typing import Optional, List, Tuple, Dict

import typer

from fastiot.cli.commands.run import _deployment_completion
from fastiot.cli.constants import FASTIOT_DEFAULT_TAG, FASTIOT_DOCKER_REGISTRY, \
    FASTIOT_NET, FASTIOT_NO_PORT_MOUNTS, DEPLOYMENTS_CONFIG_DIR
from fastiot.cli.helper_fn import get_jinja_env
from fastiot.cli.infrastructure_service_fn import get_services_list
from fastiot.cli.model import DeploymentConfig, ServiceManifest, ServiceConfig
from fastiot.cli.model.compose_info import ServiceComposeInfo
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import app, DEFAULT_CONTEXT_SETTINGS
from fastiot.env import FASTIOT_CONFIG_DIR


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

    deployment_names = _apply_checks_for_deployment_names(deployments=deployments)

    for deployment_name in deployment_names:
        deployment_dir = os.path.join(project_config.project_root_dir, project_config.build_dir, DEPLOYMENTS_CONFIG_DIR,
                                      deployment_name)
        try:
            os.makedirs(deployment_dir)
        except FileExistsError:
            pass  # No need to create directory twice

        deployment_config = project_config.deployment_by_name(name=deployment_name)

        services = _create_fastiot_services_compose_infos(deployment_config, docker_registry, tag, pull_always)
        infrastructure_services, fastiot_env = _create_infrastructure_service_compose_infos(deployment_config=deployment_config)

        with open(os.path.join(deployment_dir, 'docker-compose.yaml'), "w") as docker_compose_file:
            docker_compose_template = get_jinja_env().get_template('docker-compose.yaml.jinja')
            docker_compose_file.write(docker_compose_template.render(
                docker_net_name=net,
                environment_for_docker_compose_file=fastiot_env,
                infrastructure_services=services + infrastructure_services
            ))


def _apply_checks_for_deployment_names(deployments: List[str]) -> List[str]:
    project_config = get_default_context().project_config
    if deployments:
        deployment_names = []
        for deployment in deployments:
            if deployment not in project_config.deployment_names:
                raise ValueError(f"Deployment '{deployment}' is not in project specified.")
            if deployment not in deployment_names:
                deployment_names.append(deployment)
    else:
        deployment_names = project_config.deployment_names
    return deployment_names


def _create_fastiot_services_compose_infos(deployment_config: DeploymentConfig,
                                           docker_registry: str, tag: str, pull_always: bool
                                           ) -> List[ServiceComposeInfo]:
    project_config = get_default_context().project_config
    result = []
    for name, service_config in deployment_config.services.items():
        if service_config is None:
            service_config = ServiceConfig(image = f"{project_config.project_namespace}/{name}")

        full_image_name = _get_full_image_name(deployment_config, docker_registry, service_config, tag)
        manifest = _get_service_manifest(name, image_name=full_image_name, pull_always=pull_always)

        volumes, environment = _create_volumes(manifest)
        environment = {**environment, **service_config.environment}

        result.append(ServiceComposeInfo(name=name,
                                         image=full_image_name,
                                         environment=environment,
                                         ports=_create_ports(manifest),
                                         volumes=volumes))

    return result


def _get_full_image_name(deployment_config, docker_registry, service_config, tag):
    if service_config.docker_registry:
        local_docker_registry = service_config.docker_registry
    elif deployment_config.docker_registry:
        local_docker_registry = service_config.docker_registry
    else:
        local_docker_registry = docker_registry
    if service_config.tag:
        local_tag = service_config.tag
    elif deployment_config.tag:
        local_tag = deployment_config.tag
    else:
        local_tag = tag
    full_image_name = f"{local_docker_registry}/{service_config.image}:{local_tag}"
    return full_image_name


def _get_service_manifest(service_name: str, image_name: str, pull_always: bool) -> ServiceManifest:
    """ Return a module manifest """

    project_config = get_default_context().project_config

    if service_name in project_config.get_all_service_names():
        service = project_config.get_service_by_name(service_name)
        return service.read_manifest(check_service_name=service_name)

    # No local service => Import from docker image
    return ServiceManifest.from_docker_image(image_name, pull_always=pull_always)


def _create_ports(manifest: ServiceManifest) -> List[str]:
    ports = []
    for port in manifest.ports.values():
        external_port = int(os.environ.get(port.env_variable, str(port.port_nr)))
        ports.append(f"{external_port}:{port.port_nr}")
    return ports


def _create_volumes(manifest: ServiceManifest) -> Tuple[List[str], Dict[str, str]]:
    volumes = []
    env = {}
    for volume in manifest.volumes.values():
        volumes.append(f"{volume.location}:{volume.location}")
        env[volume.env_variable] = volume.location

    if manifest.mount_config_dir:
        volumes.append(f"./config:/etc/fastiot")
        env[FASTIOT_CONFIG_DIR] = "/etc/fastiot"

    return volumes, env


def _create_infrastructure_service_compose_infos(deployment_config: DeploymentConfig
                                                 ) -> Tuple[List[ServiceComposeInfo], Dict[str, str]]:
    services_map = get_services_list()
    result = []
    environment: Dict[str, str] = {}
    fastiot_environment: Dict[str, str] = {}
    for name, infrastructure_service_config in deployment_config.infrastructure_services.items():
        if name not in services_map:
            raise RuntimeError(f"Service with name '{name}' was not found in service list: {', '. join(services_map)}")
        service = services_map[name]

        if infrastructure_service_config.external is True:
            # External services should be skipped
            continue

        for env_var in service.environment:
            if env_var.env_var:
                value = os.environ.get(env_var.env_var, env_var.default)
                fastiot_environment[env_var.env_var] = value
            else:
                value = env_var.default
            environment[env_var.name] = value


        ports: List[str] = []
        for port in service.ports:
            external_port = os.environ.get(port.env_var, str(port.default_port_mount))
            fastiot_environment[port.env_var] = str(port.container_port)
            ports.append(f'{external_port}:{port.container_port}')

        volumes: List[str] = []
        for volume in service.volumes:
            volumes.append(f'{volume.default_volume_mount}:{volume.container_volume}')

        result.append(ServiceComposeInfo(
            name=service.name,
            image=service.image,
            environment=environment,
            ports=ports,
            volumes=volumes
        ))
    return result, fastiot_environment
