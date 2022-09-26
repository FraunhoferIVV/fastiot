import logging
import os
import shutil
from typing import Optional, List, Tuple, Dict

import typer

from fastiot.cli.commands.deploy import _deployment_completion
from fastiot.cli.constants import FASTIOT_DEFAULT_TAG, FASTIOT_DOCKER_REGISTRY, \
    FASTIOT_NET, DEPLOYMENTS_CONFIG_DIR, FASTIOT_PORT_OFFSET, FASTIOT_PULL_ALWAYS
from fastiot.cli.helper_fn import get_jinja_env, parse_env_file
from fastiot.cli.infrastructure_service_fn import get_infrastructure_service_ports_monotonically_increasing, get_infrastructure_service_ports_randomly
from fastiot.cli.model import DeploymentConfig, ServiceManifest, ServiceConfig
from fastiot.cli.model.compose_info import ServiceComposeInfo
from fastiot.cli.model.context import get_default_context
from fastiot.cli.model.service import InfrastructureService
from fastiot.cli.typer_app import app, DEFAULT_CONTEXT_SETTINGS
from fastiot.env import FASTIOT_CONFIG_DIR


@app.command(context_settings=DEFAULT_CONTEXT_SETTINGS)
def config(deployments: List[str] = typer.Argument(default=[],
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

    project_config = get_default_context().project_config

    if use_test_deployment:
        if not project_config.integration_test_deployment:
            logging.warning("No `integration_test_deployment` configured. Exiting configure.")
            raise typer.Exit(1)
        deployments = [project_config.integration_test_deployment]

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
        deployment_dir = os.path.join(project_config.project_root_dir, project_config.build_dir, DEPLOYMENTS_CONFIG_DIR,
                                      deployment_name)
        shutil.rmtree(deployment_dir, ignore_errors=True)
        os.makedirs(deployment_dir, exist_ok=True)

        env_filename = os.path.join(project_config.project_root_dir, DEPLOYMENTS_CONFIG_DIR, deployment_name, '.env')
        if os.path.isfile(env_filename):
            env = parse_env_file(env_filename)
            for name, value in env.items():
                if name not in infrastructure_ports and name not in os.environ:
                    os.environ[name] = str(value)
        else:
            env = {}

        deployment_config = project_config.deployment_by_name(name=deployment_name)
        env_service_internal_modifications = {}
        infrastructure_services = _create_infrastructure_service_compose_infos(
            env=env,
            env_service_internal_modifications_out=env_service_internal_modifications,
            deployment_config=deployment_config,
            is_test_deployment=deployment_name == project_config.integration_test_deployment
        )
        services = _create_services_compose_infos(
            env=env,
            deployment_config=deployment_config,
            docker_registry=docker_registry,
            tag=tag,
            pull_always=pull_always
        )

        deployment_source_dir = os.path.join(project_config.project_root_dir, DEPLOYMENTS_CONFIG_DIR, deployment_name)
        shutil.copytree(deployment_source_dir, deployment_dir, dirs_exist_ok=True,
                        ignore=lambda _, __: ['deployment.yaml', 'dev-overwrite.env'])

        with open(os.path.join(deployment_dir, 'docker-compose.yaml'), "w") as docker_compose_file:
            docker_compose_template = get_jinja_env().get_template('docker-compose.yaml.jinja')
            docker_compose_file.write(docker_compose_template.render(
                docker_net_name=net,
                environment_for_docker_compose_file=fastiot_env,
                services=services + infrastructure_services,
                env_file=os.path.isfile(env_filename)
            ))

    logging.info("Successfully created configurations!")


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


def _create_services_compose_infos(env: Dict[str, str],
                                   deployment_config: DeploymentConfig,
                                   docker_registry: str,
                                   tag: str,
                                   pull_always: bool
                                   ) -> List[ServiceComposeInfo]:
    project_config = get_default_context().project_config
    result = []
    for name, service_config in deployment_config.services.items():
        if service_config is None:
            service_config = ServiceConfig(image=f"{project_config.project_namespace}/{name}")

        full_image_name = _get_full_image_name(deployment_config, docker_registry, service_config, tag)
        manifest = _get_service_manifest(name, image_name=full_image_name, pull_always=pull_always)

        volumes, volumes_env = _create_volumes(manifest)
        ports, ports_env = _create_ports(manifest)
        devices, devices_env = _create_devices(manifest)
        environment = {**devices_env, **volumes_env, **ports_env, **service_config.environment}

        result.append(ServiceComposeInfo(name=name,
                                         image=full_image_name,
                                         environment=environment,
                                         ports=ports,
                                         volumes=volumes,
                                         devices=devices,
                                         privileged=manifest.privileged))

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


def _create_ports(env: Dict[str, str], manifest: ServiceManifest) -> Tuple[List[str], Dict[str, str]]:
    ports = []
    env = {}
    for port in manifest.ports.values():
        external_port = int(os.environ.get(port.env_variable, str(port.port_nr)))
        ports.append(f"{external_port}:{port.port_nr}")
        env[port.env_variable] = str(port.port_nr)

    return ports, env


def _create_volumes(env: Dict[str, str], manifest: ServiceManifest) -> Tuple[List[str], Dict[str, str]]:
    volumes = []
    env = {}
    for volume in manifest.volumes.values():
        volumes.append(f"{volume.location}:{volume.location}")
        env[volume.env_variable] = volume.location

    if manifest.mount_config_dir:
        volumes.append("./config:/etc/fastiot")
        env[FASTIOT_CONFIG_DIR] = "/etc/fastiot"

    return volumes, env


def _create_devices(env: Dict[str, str], manifest: ServiceManifest) -> Tuple[List[str], Dict[str, str]]:
    devices = []
    env = {}
    for device in manifest.devices.values():
        devices.append(f"{device.location}:{device.location}")
        env[device.env_variable] = device.location

    return devices, env


def _create_infrastructure_service_compose_infos(env: Dict[str, str],
                                                 env_service_internal_modifications_out: Dict[str, str],
                                                 deployment_config: DeploymentConfig,
                                                 is_test_deployment: bool
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

        service_environment: Dict[str, str] = {}
        for env_var in service.environment:
            if env_var.env_var:
                value = env.get(env_var.env_var, env_var.default)
                env[env_var.env_var] = value
            else:
                value = env_var.default
            service_environment[env_var.name] = value
        env_service_internal_modifications_out[service.host_name_env_var] = name
        if service.host_name_env_var not in env:
            env[service.host_name_env_var] = 'localhost'

        ports: List[str] = []
        for port in service.ports:
            external_port = env.get(port.env_var, str(port.default_port_mount))
            env[port.env_var] = external_port
            ports.append(f'{external_port}:{port.container_port}')
            env_service_internal_modifications_out[port.env_var] = str(port.container_port)

        if not is_test_deployment:
            volumes = [f'{v.default_volume_mount}:{v.container_volume}' if v.default_volume_mount == os.environ.get(
                v.env_var) else f'{os.environ.get(v.env_var)}:{v.container_volume}' for v in service.volumes]
            tmpfs: List[str] = []
        else:
            volumes = []
            tmpfs = [v.container_volume for v in service.volumes]

        result.append(ServiceComposeInfo(
            name=service.name,
            image=service.image,
            environment=service_environment,
            ports=ports,
            volumes=volumes,
            tmpfs=tmpfs
        ))
    return result

