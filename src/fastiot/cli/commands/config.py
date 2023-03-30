import logging
import os
import shutil
from typing import Optional, List, Dict

import typer
import yaml

from fastiot.cli.commands.deploy import _deployment_completion
from fastiot.cli.constants import FASTIOT_DEFAULT_TAG, FASTIOT_DOCKER_REGISTRY, \
    FASTIOT_NET, DEPLOYMENTS_CONFIG_DIR, FASTIOT_PORT_OFFSET, FASTIOT_PULL_ALWAYS, FASTIOT_USE_PORT_IMPORT
from fastiot.cli.helper_fn import get_jinja_env
from fastiot.cli.infrastructure_service_fn import get_infrastructure_service_ports_monotonically_increasing, \
    get_infrastructure_service_ports_randomly
from fastiot.cli.model import DeploymentConfig, ServiceManifest, ServiceConfig
from fastiot.cli.model.compose_info import ServiceComposeInfo
from fastiot.cli.model.infrastructure_service import InfrastructureService
from fastiot.cli.model.manifest import MountConfigDirEnum
from fastiot.cli.model.project import ProjectContext
from fastiot.cli.typer_app import app, DEFAULT_CONTEXT_SETTINGS
from fastiot.env import env_basic
from fastiot.env.env_constants_basic import FASTIOT_CONFIG_DIR, FASTIOT_VOLUME_DIR


@app.command(context_settings=DEFAULT_CONTEXT_SETTINGS)
def config(deployments: Optional[List[str]] = typer.Argument(default=None,
                                                             shell_complete=_deployment_completion,
                                                             help="The deployment configs to generate. "
                                                                  "Default: all configs"),
           tag: str = typer.Option('latest', '-t', '--tag',
                                   help="Specify a default tag for the deployment(s). Applies to all images not "
                                        "further defined with image etc.",
                                   envvar=FASTIOT_DEFAULT_TAG),
           docker_registry: str = typer.Option('', '-r', '--docker-registry',
                                               help="Specify a default docker registry for the deployment(s)",
                                               envvar=FASTIOT_DOCKER_REGISTRY),
           net: str = typer.Option("fastiot-net", '-n', '--net',
                                   help="The name of the network for all services.",
                                   envvar=FASTIOT_NET),
           pull_always: bool = typer.Option(False, '--pull-always',
                                            help="If given, it will always use 'docker pull' command to pull images "
                                                 "from specified docker registries before reading manifest.yaml files.",
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
                                                     envvar=FASTIOT_PORT_OFFSET),
           use_port_import: bool = typer.Option(True,
                                                help="If this is set to True (default), it will try to import port "
                                                     "mounts from .env-file from build and use them if possible. Port "
                                                     "offset is ignored for imported ports.",
                                                envvar=FASTIOT_USE_PORT_IMPORT)):
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
        logging.error("Port offset must be greater or equal zero. It is %s instead", str(port_offset))
        raise typer.Exit(1)

    context: ProjectContext = ProjectContext.default

    if use_test_deployment:
        if not context.integration_test_deployment:
            logging.warning("No `integration_test_deployment` configured. Exiting configure.")
            raise typer.Exit(0)
        deployments = [context.integration_test_deployment]

    if deployments:
        deployment_names = _apply_checks_for_deployment_names(deployments=deployments)
    else:
        deployment_names = context.deployment_names

    # This will set environment variables for externally opened ports, usually to be used for integration tests but also
    # to access the services externally. When creating the compose infos for infrastructure services the env vars will
    # be used, so no further access to the settings is needed.
    if port_offset is None:
        infrastructure_ports = {}
    elif port_offset == 0:
        infrastructure_ports = get_infrastructure_service_ports_randomly()
    else:
        infrastructure_ports = get_infrastructure_service_ports_monotonically_increasing(offset=port_offset)

    if not isinstance(net, str):  # Workaround for https://github.com/tiangolo/typer/issues/106
        net = net.default

    for deployment_name in deployment_names:
        if use_port_import:  # We read in any previously set ports for the deployment in the build dir
            temp_build_env = context.build_env_for_deployment(deployment_name)
            for key, value in [(k, v) for k, v in temp_build_env.items() if k in infrastructure_ports]:
                infrastructure_ports[key] = int(value)

        deployment_build_dir = context.deployment_build_dir(name=deployment_name)
        shutil.rmtree(deployment_build_dir, ignore_errors=True)
        os.makedirs(deployment_build_dir, exist_ok=True)

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
            is_integration_test_deployment=deployment_name == context.integration_test_deployment,
            project_namespace=context.project_namespace
        )
        services = _create_services_compose_infos(
            env=env,
            env_additions=env_additions,
            deployment_config=deployment_config,
            docker_registry=docker_registry,
            tag=tag,
            pull_always=pull_always
        )

        if deployment_config.config_dir and FASTIOT_CONFIG_DIR not in env:
            env_additions[FASTIOT_CONFIG_DIR] = os.path.join(context.deployment_dir(name=deployment_name),
                                                             deployment_config.config_dir)

        # Adjust relative paths in env_additions
        for key, value in env_additions.items():
            if value.startswith('./'):
                env_additions[key] = os.path.join(context.deployment_dir(name=deployment_name), value)


        shutil.copytree(context.deployment_dir(name=deployment_name), deployment_build_dir, dirs_exist_ok=True,
                        ignore=lambda _, __: ['deployment.yaml', '.env'])

        with open(os.path.join(deployment_build_dir, 'docker-compose.yaml'), "w") as docker_compose_file:
            docker_compose_template = get_jinja_env().get_template('docker-compose.yaml.j2')
            docker_compose_file.write(docker_compose_template.render(
                docker_net_name=net,
                environment_for_docker_compose_file=env_service_internal_modifications,
                services=services + infrastructure_services,
                env_file=env or env_additions
            ))

        env_filename = context.env_file_for_deployment(name=deployment_name)
        env_file_content = ""
        if os.path.exists(env_filename):
            with open(env_filename, "r") as env_file:
                env_file_content = env_file.read()

        with open(context.build_env_file_for_deployment(name=deployment_name), "w") as env_file:
            env_file.write(
                f"# Note: This file is generated. Please do not modify this file but instead go to the .env-file "
                f"located at \n"
                f"# '{env_filename}'.\n\n")

            if env_file_content.strip() != '':
                env_file.write("# The following content has been copied from there:\n\n")
                env_file.write(env_file_content)
            else:
                env_file.write("# Currently this file is empty or non-existent so there is nothing to copy from "
                               "there.\n")

            if env_additions:
                env_file.write("\n# The following content has been injected via fastiot cli:\n")
                for key, value in env_additions.items():
                    env_file.write(f"\n{key}={value}")
                env_file.write("\n")  # ending files with '\n' as it is a best practice for file management under linux

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
                                   env_additions: Dict[str, str],
                                   deployment_config: DeploymentConfig,
                                   docker_registry: str,
                                   tag: str,
                                   pull_always: bool
                                   ) -> List[ServiceComposeInfo]:
    context: ProjectContext = ProjectContext.default
    result = []
    for name, service_config in deployment_config.services.items():
        if service_config is None:
            # This can only be the case for internal services as external ones need to define the image
            # We set the tag here for internal services.
            service_config = ServiceConfig(image=f"{context.project_namespace}/{name}", tag=tag)

        full_image_name = _get_full_image_name(deployment_config, docker_registry, service_config)
        manifest = _get_service_manifest(name, image_name=full_image_name, pull_always=pull_always)

        service_env = {**service_config.environment}
        volumes = _create_volumes(env, env_additions, service_env, deployment_config.config_dir, manifest)
        ports = _create_ports(env, service_env, manifest)
        devices = _create_devices(env, service_env, manifest)
        extras = _create_compose_extras(manifest)

        result.append(ServiceComposeInfo(name=name,
                                         image=full_image_name,
                                         environment=service_env,
                                         ports=ports,
                                         volumes=volumes,
                                         devices=devices,
                                         privileged=manifest.privileged,
                                         extras=extras))
    return result


def _get_full_image_name(deployment_config: DeploymentConfig,
                         docker_registry: str,
                         service_config: ServiceConfig):
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
        temp_tag = ""

    full_image_name = service_config.image
    if temp_docker_registry:
        full_image_name = f"{temp_docker_registry}/{full_image_name}"
    if temp_tag:
        full_image_name = f"{full_image_name}:{temp_tag}"

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


def _create_volumes(env: Dict[str, str], env_additions: Dict[str, str], service_env: Dict[str, str],
                    config_dir: str, manifest: ServiceManifest) -> List[str]:
    volumes = []
    for volume in manifest.volumes:
        if env.get(volume.env_variable) == "":
            continue
        external_volume = env.get(volume.env_variable, volume.location)
        volumes.append(f"{external_volume}:{volume.location}")
        # We use the default location inside the container as possible relative paths will make trouble there.
        service_env[volume.env_variable] = volume.location
        # The env var inside the container will point at the right location
        env_additions[volume.env_variable] = external_volume
        # Externally we point to the env var specified path, to be made absolute on the system later on

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


def _create_compose_extras(manifest: ServiceManifest) -> str:
    if manifest.compose_extras:
        return yaml.dump(manifest.compose_extras).rstrip()
    return ""


def _create_infrastructure_service_compose_infos(env: Dict[str, str],
                                                 env_additions: Dict[str, str],
                                                 env_service_internal_modifications: Dict[str, str],
                                                 infrastructure_ports: Dict[str, int],
                                                 deployment_config: DeploymentConfig,
                                                 is_integration_test_deployment: bool,
                                                 project_namespace: str
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
                if env_var.env_var not in env:
                    # add env var if not available so that default is always set
                    env_additions[env_var.env_var] = value
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
        service_temp_volumes: List[str] = []
        for volume in service.volumes:
            root_volume = env.get(FASTIOT_VOLUME_DIR, env_basic.volume_dir)
            value = 'tmpfs'
            if not is_integration_test_deployment or not volume.tmpfs_for_tests:
                # set default for none integration test volumes
                if volume.default_volume_mount is None:
                    value = f"{root_volume}/{project_namespace}/{deployment_config.name}/{name}"
                else:
                    value = volume.default_volume_mount

            if volume.env_var:
                if volume.env_var in env:
                    # set configured volume
                    value = env[volume.env_var]
                    if value != 'tmpfs' and value != '' and value[0] != '/' and not value.startswith('./'):
                        value = os.path.join(root_volume, value)

            if value == 'tmpfs':
                service_temp_volumes.append(volume.container_volume)
            elif value:
                service_volumes.append(f'{value}:{volume.container_volume}')

        service_extensions = ""
        for extension in service.compose_extras:
            option = extension.option_name
            if extension.env_var and extension.env_var in env:
                value = env[extension.env_var]
            else:
                value = extension.default_value

            if value:
                service_extensions += f'{option}: {value}\n'
        service_extensions = service_extensions.rstrip()

        result.append(ServiceComposeInfo(
            name=service.name,
            image=service.image,
            environment=service_environment,
            ports=service_ports,
            volumes=service_volumes,
            tmpfs=service_temp_volumes,
            extras=service_extensions
        ))
    return result
