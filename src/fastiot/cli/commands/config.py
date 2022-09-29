import logging
import os
import shutil
from typing import Optional, List, Tuple, Dict

import typer

from fastiot.cli.commands.deploy import _deployment_completion
from fastiot.cli.constants import FASTIOT_DEFAULT_TAG, FASTIOT_DOCKER_REGISTRY, \
    FASTIOT_NET, DEPLOYMENTS_CONFIG_DIR, FASTIOT_PORT_OFFSET, FASTIOT_PULL_ALWAYS
from fastiot.cli.helper_fn import get_jinja_env
from fastiot.cli.infrastructure_service_fn import get_infrastructure_service_ports_monotonically_increasing, get_infrastructure_service_ports_randomly
from fastiot.cli.model import DeploymentConfig, ServiceManifest, ServiceConfig
from fastiot.cli.model.compose_info import ServiceComposeInfo
from fastiot.cli.model.manifest import MountConfigDirEnum
from fastiot.cli.model.project import ProjectContext
from fastiot.cli.model.service import InfrastructureService
from fastiot.cli.typer_app import app, DEFAULT_CONTEXT_SETTINGS
from fastiot.env import FASTIOT_CONFIG_DIR


@app.command(context_settings=DEFAULT_CONTEXT_SETTINGS)
def config(deployments: Optional[List[str]] = typer.Argument(default=None,
                                                             shell_complete=_deployment_completion,
                                                             help="The deployment configs to generate. Default: all configs"),
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
                                                 "files.",
                                            envvar=FASTIOT_PULL_ALWAYS),
           use_test_deployment: bool = typer.Option(False,
                                                    help="Create only the configuration for the integration "
                                                         "test deployment."),
           port_offset: Optional[int] = typer.Option(None,
                                                     help="Set this to create a docker-compose file with "
                                                          "custom ports for infrastructure services. "
                                                          "Especially when running multiple deployments "
                                                          "(e.g. on a CI runner) this comes handy. The "
                                                          "first service will have the selected port, "
                                                          "every following service one port number "
                                                          "higher.\n You may set this to 0 to get "
                                                          "random, available ports instead.",
                                                     envvar=FASTIOT_PORT_OFFSET)):
    """
    This command generates deployment configs. Per default, it generates all configs. Optionally, you can specify a
    config to only generate a single deployment config. All generated files will be placed inside the build dir of your
    project.

    For each service the docker images will be executed to import the manifest.yaml file. Therefore, if you want to
    build one or more deployments you have to be logged in and connected to the corresponding docker registries or build
    the images locally.
    """

    logging.info("Creating configurations…")

    if port_offset and port_offset < 0:
        raise ValueError(f"Port offset must be greater or equal zero. It is {port_offset} instead")

    context = ProjectContext.default

    if use_test_deployment:
        if not context.integration_test_deployment:
            logging.warning("No `integration_test_deployment` configured. Exiting configure.")
            raise typer.Exit(1)
        deployments = [context.integration_test_deployment]

    deployment_names = _apply_checks_for_deployment_names(deployments=deployments)

    # This will set environment variables for externally opened ports, usually to be used for integration tests but also
    # to access the services externally. When creating the compose infos for infrastructure services the env vars will
    # be used, so no further access to the settings is needed.
    if port_offset is None:
        infrastructure_ports = {}
    elif port_offset == 0:
        infrastructure_ports = get_infrastructure_service_ports_randomly()
    else:
        infrastructure_ports = get_infrastructure_service_ports_monotonically_increasing(offset=port_offset)

    for deployment_name in deployment_names:
        deployment_dir = context.deployment_build_dir(name=deployment_name)
        shutil.rmtree(deployment_dir, ignore_errors=True)
        os.makedirs(deployment_dir, exist_ok=True)

        env = context.env_for_deployment(name=deployment_name)
        deployment_config = context.deployment_by_name(name=deployment_name)
        env_additions = {}
        env_service_internal_modifications = {}
        infrastructure_services = _create_infrastructure_service_compose_infos(
            env=env,
            env_additions=env_additions,
            env_service_internal_modifications=env_service_internal_modifications,
            infrastructure_ports=infrastructure_ports,
            deployment_config=deployment_config,
        )
        services = _create_services_compose_infos(
            env=env,
            deployment_config=deployment_config,
            docker_registry=docker_registry,
            tag=tag,
            pull_always=pull_always
        )

        deployment_source_dir = os.path.join(context.project_root_dir, DEPLOYMENTS_CONFIG_DIR, deployment_name)
        shutil.copytree(deployment_source_dir, deployment_dir, dirs_exist_ok=True, ignore=lambda _, __: ['deployment.yaml'])

        with open(os.path.join(deployment_dir, 'docker-compose.yaml'), "w") as docker_compose_file:
            docker_compose_template = get_jinja_env().get_template('docker-compose.yaml.jinja')
            docker_compose_file.write(docker_compose_template.render(
                docker_net_name=net,
                environment_for_docker_compose_file=env_service_internal_modifications,
                services=services + infrastructure_services,
                env_file=env or env_additions
            ))
        if env_additions:
            with open(os.path.join(deployment_dir, '.env'), "a") as env_file:
                for key, value in env_additions.items():
                    env_file.write(f"\n{key}={value}")

    logging.info("Successfully created configurations!")


def _apply_checks_for_deployment_names(deployments: List[str]) -> List[str]:
    context = ProjectContext.default
    if deployments:
        deployment_names = []
        for deployment in deployments:
            if deployment not in context.deployment_names:
                raise ValueError(f"Deployment '{deployment}' is not in project specified.")
            if deployment not in deployment_names:
                deployment_names.append(deployment)
    else:
        deployment_names = context.deployment_names
    return deployment_names


def _create_services_compose_infos(env: Dict[str, str],
                                   deployment_config: DeploymentConfig,
                                   docker_registry: str,
                                   tag: str,
                                   pull_always: bool
                                   ) -> List[ServiceComposeInfo]:
    context = ProjectContext.default
    result = []
    for name, service_config in deployment_config.services.items():
        if service_config is None:
            service_config = ServiceConfig(image=f"{context.project_namespace}/{name}")

        full_image_name = _get_full_image_name(deployment_config, docker_registry, service_config, tag)
        manifest = _get_service_manifest(name, image_name=full_image_name, pull_always=pull_always)

        service_env = {**service_config.environment}
        volumes = _create_volumes(env, service_env, deployment_config.config_dir, manifest)
        ports = _create_ports(env, service_env, manifest)
        devices = _create_devices(env, service_env, manifest)

        result.append(ServiceComposeInfo(name=name,
                                         image=full_image_name,
                                         environment=service_env,
                                         ports=ports,
                                         volumes=volumes,
                                         devices=devices,
                                         privileged=manifest.privileged))
    return result


def _get_full_image_name(deployment_config, docker_registry, service_config, tag):
    if service_config.docker_registry:
        temp_docker_registry = service_config.docker_registry
    elif deployment_config.docker_registry:
        temp_docker_registry = service_config.docker_registry
    else:
        temp_docker_registry = docker_registry
    if service_config.tag:
        temp_tag = service_config.tag
    elif deployment_config.tag:
        temp_tag = deployment_config.tag
    else:
        temp_tag = tag
    full_image_name = f"{temp_docker_registry}/{service_config.image}:{temp_tag}"
    return full_image_name


def _get_service_manifest(service_name: str, image_name: str, pull_always: bool) -> ServiceManifest:
    """ Return a module manifest """

    context = ProjectContext.default

    if service_name in context.get_all_service_names():
        service = context.get_service_by_name(service_name)
        return service.read_manifest(check_service_name=service_name)

    # No local service => Import from docker image
    return ServiceManifest.from_docker_image(image_name, pull_always=pull_always)


def _create_ports(env: Dict[str, str], service_env: Dict[str, str], manifest: ServiceManifest) -> List[str]:
    ports = []
    for port in manifest.ports:
        external_port = int(env.get(port.env_variable, str(port.port)))
        ports.append(f"{external_port}:{external_port}")
        service_env[port.env_variable] = str(external_port)
    return ports


def _create_volumes(env: Dict[str, str], service_env: Dict[str, str], config_dir: str, manifest: ServiceManifest) -> List[str]:
    volumes = []
    for volume in manifest.volumes:
        external_volume = env.get(volume.env_variable, volume.location)
        volumes.append(f"{external_volume}:{external_volume}")
        service_env[volume.env_variable] = external_volume

    if manifest.mount_config_dir in [MountConfigDirEnum.required, MountConfigDirEnum.optional] and config_dir:
        volumes.append(f"{config_dir}:/etc/fastiot")
        service_env[FASTIOT_CONFIG_DIR] = "/etc/fastiot"
    elif manifest.mount_config_dir is MountConfigDirEnum.required:
        raise ValueError(f"Config dir is required for service {manifest.name}")

    return volumes


def _create_devices(env: Dict[str, str], service_env: Dict[str, str], manifest: ServiceManifest) -> List[str]:
    devices = []
    for device in manifest.devices:
        external_device = env.get(device.env_variable, device.location)
        devices.append(f"{external_device}:{external_device}")
        service_env[device.env_variable] = device.location

    return devices


def _create_infrastructure_service_compose_infos(env: Dict[str, str],
                                                 env_additions: Dict[str, str],
                                                 env_service_internal_modifications: Dict[str, str],
                                                 infrastructure_ports: Dict[str, int],
                                                 deployment_config: DeploymentConfig,
                                                 ) -> List[ServiceComposeInfo]:
    services_map = InfrastructureService.all
    result = []

    for name, infrastructure_service_config in deployment_config.infrastructure_services.items():

        if name not in services_map:
            raise RuntimeError(f"Service with name '{name}' was not found in service list: {', '.join(services_map)}")
        service = services_map[name]

        if infrastructure_service_config.external is True:
            # External services should be skipped
            continue

        env_service_internal_modifications[service.host_name_env_var] = name
        if service.host_name_env_var not in env:
            env_additions[service.host_name_env_var] = 'localhost'

        service_environment: Dict[str, str] = {}
        for env_var in service.environment:
            if env_var.env_var:
                value = env.get(env_var.env_var, env_var.default)
            else:
                value = env_var.default
            service_environment[env_var.name] = value

        service_ports: List[str] = []
        for port in service.ports:
            if port.env_var:
                value = env.get(port.env_var, str(port.default_port_mount))
                value = str(infrastructure_ports.get(port.env_var, value))
            else:
                value = str(port.default_port_mount)
            if port.env_var not in env:
                env_additions[port.env_var] = value
                env_service_internal_modifications[port.env_var] = str(port.container_port)
            service_ports.append(f'{value}:{port.container_port}')

        service_volumes: List[str] = []
        service_temp_volumes : List[str] = []
        for volume in service.volumes:
            if volume.env_var:
                value = env.get(volume.env_var, str(volume.default_volume_mount))
            else:
                value = str(volume.default_volume_mount)

            if value == 'tmpfs':
                service_temp_volumes.append(volume.container_volume)
            else:
                service_volumes.append(f'{value}:{volume.container_volume}')

        result.append(ServiceComposeInfo(
            name=service.name,
            image=service.image,
            environment=service_environment,
            ports=service_ports,
            volumes=service_volumes,
            tmpfs=service_temp_volumes
        ))
    return result

