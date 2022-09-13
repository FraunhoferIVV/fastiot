import logging
import os
import shutil
from typing import Optional, List, Tuple, Dict

import typer

from fastiot.cli.commands.deploy import _deployment_completion
from fastiot.cli.constants import FASTIOT_DEFAULT_TAG, FASTIOT_DOCKER_REGISTRY, \
    FASTIOT_NET, DEPLOYMENTS_CONFIG_DIR
from fastiot.cli.helper_fn import get_jinja_env, parse_env_file
from fastiot.cli.infrastructure_service_fn import get_services_list, set_infrastructure_service_port_environment
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
           test_deployment_only: bool = typer.Option(False, help="Create only the configuration for the integration "
                                                                 "test deployment."),
           service_port_offset: Optional[int] = typer.Option(0, help="Set this to create a docker-compose file with "
                                                                     "custom ports for infrastructure services. "
                                                                     "Especially when running multiple deployments "
                                                                     "(e.g. on a CI runner) this comes handy. The "
                                                                     "first service will have the selected port, "
                                                                     "every following service one port number "
                                                                     "higher.\n You may set this to -1 to get "
                                                                     "random, available ports instead."),
           generated_py_with_internal_hostnames: Optional[bool] = typer.Option(False,
                                                                               help="This is especially for the CI "
                                                                                    "runner. It will create the "
                                                                                    "generated.py to set up env vars "
                                                                                    "for tests with docker-internal "
                                                                                    "hostnames, e.g. nats for the "
                                                                                    "broker.")
           ):
    """
    This command generates deployment configs. Per default, it generates all configs. Optionally, you can specify a
    config to only generate a single deployment config. All generated files will be placed inside the build dir of your
    project.

    For each service the docker images will be executed to import the manifest.yaml file. Therefore, if you want to
    build one or more deployments you have to be logged in and connected to the corresponding docker registries or build
    the images locally.
    """

    logging.info("Creating configurations…")

    project_config = get_default_context().project_config

    if test_deployment_only:
        if not project_config.integration_test_deployment:
            logging.warning("No `integration_test_deployment` configured. Exiting configure.")
            raise typer.Exit(0)
        deployments = [project_config.integration_test_deployment]

    deployment_names = _apply_checks_for_deployment_names(deployments=deployments)

    # This will set environment variables for externally opened ports, usually to be used for integration tests but also
    # to access the services externally. When creating the compose infos for infrastructure services the env vars will
    # be used, so no further access to the settings is needed.
    if service_port_offset == -1:
        infrastructure_ports = set_infrastructure_service_port_environment(random=True)
    elif service_port_offset > 0:  # Use defined something
        infrastructure_ports = set_infrastructure_service_port_environment(offset=service_port_offset)
    else:  # No overwrites to be done
        infrastructure_ports = {}

    original_os_env = os.environ.copy()

    for deployment_name in deployment_names:
        deployment_dir = os.path.join(project_config.project_root_dir, project_config.build_dir, DEPLOYMENTS_CONFIG_DIR,
                                      deployment_name)
        os.environ = original_os_env.copy()
        shutil.rmtree(deployment_dir, ignore_errors=True)
        os.makedirs(deployment_dir, exist_ok=True)

        env_filename = os.path.join(project_config.project_root_dir, DEPLOYMENTS_CONFIG_DIR, deployment_name, '.env')
        if os.path.isfile(env_filename):
            env_file_env = parse_env_file(env_filename)
            for name, value in env_file_env.items():
                if name not in infrastructure_ports and name not in os.environ:
                    os.environ[name] = str(value)
        else:
            env_file_env = {}

        deployment_config = project_config.deployment_by_name(name=deployment_name)

        services = _create_fastiot_services_compose_infos(deployment_config, docker_registry, tag, pull_always)
        infrastructure_services, fastiot_env, tests_env = _create_infrastructure_service_compose_infos(
            deployment_config=deployment_config,
            generated_py_with_internal_hostnames=generated_py_with_internal_hostnames,
            is_test_deployment=deployment_name == project_config.integration_test_deployment)

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

        if deployment_name == project_config.integration_test_deployment:
            _create_generated_py(project_config, env_file_env, fastiot_env, tests_env)

        logging.info("Successfully created configurations!")


def _create_generated_py(project_config, env_file_env, fastiot_env, tests_env):
    environment = {**env_file_env, **fastiot_env, **tests_env}
    environment = {k: environment[k] for k in sorted(environment.keys())}
    with open(os.path.join(project_config.project_root_dir, "src",
                           project_config.test_package, 'generated.py'), "w") as generated_file:
        generated_template = get_jinja_env().get_template('test_env.py.jinja')
        generated_file.write(generated_template.render(
            env_vars=str(environment).replace(",", ",\n               "))
        )


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


def _create_ports(manifest: ServiceManifest) -> Tuple[List[str], Dict[str, str]]:
    ports = []
    env = {}
    for port in manifest.ports.values():
        external_port = int(os.environ.get(port.env_variable, str(port.port_nr)))
        ports.append(f"{external_port}:{port.port_nr}")
        env[port.env_variable] = str(port.port_nr)

    return ports, env


def _create_volumes(manifest: ServiceManifest) -> Tuple[List[str], Dict[str, str]]:
    volumes = []
    env = {}
    for volume in manifest.volumes.values():
        volumes.append(f"{volume.location}:{volume.location}")
        env[volume.env_variable] = volume.location

    if manifest.mount_config_dir:
        volumes.append("./config:/etc/fastiot")
        env[FASTIOT_CONFIG_DIR] = "/etc/fastiot"

    return volumes, env


def _create_devices(manifest: ServiceManifest) -> Tuple[List[str], Dict[str, str]]:
    devices = []
    env = {}
    for device in manifest.devices.values():
        devices.append(f"{device.location}:{device.location}")
        env[device.env_variable] = device.location

    return devices, env


def _create_infrastructure_service_compose_infos(deployment_config: DeploymentConfig,
                                                 generated_py_with_internal_hostnames: bool,
                                                 is_test_deployment: bool
                                                 ) -> Tuple[List[ServiceComposeInfo], Dict[str, str], Dict[str, str]]:
    services_map = get_services_list()
    result = []

    fastiot_environment: Dict[str, str] = {}
    tests_environment: Dict[str, str] = {}
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
                value = os.environ.get(env_var.env_var, env_var.default)
                fastiot_environment[env_var.env_var] = value
            else:
                value = env_var.default
            service_environment[env_var.name] = value
        if generated_py_with_internal_hostnames:
            tests_environment[service.host_name_env_var] = name
        else:
            tests_environment[service.host_name_env_var] = 'localhost'

        ports: List[str] = []
        for port in service.ports:
            external_port = os.environ.get(port.env_var, str(port.default_port_mount))
            fastiot_environment[port.env_var] = str(port.container_port)
            ports.append(f'{external_port}:{port.container_port}')
            if generated_py_with_internal_hostnames:
                tests_environment[port.env_var] = str(port.container_port)
            else:
                tests_environment[port.env_var] = str(external_port)

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
    return result, fastiot_environment, tests_environment
