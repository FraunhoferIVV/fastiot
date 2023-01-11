""" Build command """
import logging
import os
import os.path
import re
import subprocess
from glob import glob
from typing import List, Optional
from shutil import copyfile

import typer
from pydantic import BaseModel

from fastiot.cli.constants import BUILD_MODES, BUILDER_NAME, FASTIOT_DOCKER_REGISTRY, FASTIOT_DOCKER_REGISTRY_CACHE, \
    MANIFEST_FILENAME, DOCKER_BUILD_DIR
from fastiot.cli.env import env_cli
from fastiot.cli.helper_fn import get_jinja_env
from fastiot.cli.model import ProjectContext, ServiceManifest, CPUPlatform, Service
from fastiot.cli.model.docker_template import DockerTemplate
from fastiot.cli.typer_app import app, DEFAULT_CONTEXT_SETTINGS


def _mode_completion(*args, **kwargs) -> List[str]:
    return BUILD_MODES


def _mode_callback(mode: str):
    if mode not in _mode_completion():
        raise typer.BadParameter(f"Mode must be 'debug' or 'release'. But it is {mode}")
    return mode


def _services_completion() -> List[str]:
    return [os.path.basename(os.path.dirname(m)) for m in list(glob("src/*/*/" + MANIFEST_FILENAME))]


def _platform_completion() -> List[str]:
    return [p.value for p in CPUPlatform]


@app.command(context_settings=DEFAULT_CONTEXT_SETTINGS)
def build(services: Optional[List[str]] = typer.Argument(None, help="The services to build. Default: all services",
                                                         shell_complete=_services_completion),
          mode: str = typer.Option('debug', '-m', '--mode',
                                   callback=_mode_callback, shell_complete=_mode_completion,
                                   help="The build mode for docker images. Can be 'debug' or 'release'. "
                                        "No compilation of python code will happen if chosen 'debug'. Nuitka "
                                        "compilation will be applied if chosen 'release'."),
          tag: str = typer.Option('latest', '-t', '--tag',
                                  help="The tags to use for building as a comma ',' separated list."),
          docker_registry: str = typer.Option('', '-r', '--docker-registry',
                                              envvar=FASTIOT_DOCKER_REGISTRY,
                                              help="The docker registry to be used for tagging. If docker_registry is "
                                                   "unspecified, it will look for a process environment variable "
                                                   "FASTIOT_DOCKER_REGISTRY. If docker registry is not empty, the "
                                                   "built image names will begin with the docker registry followed by "
                                                   "a slash."),
          docker_registry_cache: str = typer.Option('', '-c', '--docker-registry-cache',
                                                    envvar=FASTIOT_DOCKER_REGISTRY_CACHE,
                                                    help="The docker registry cache. If docker registry cache is "
                                                         "unspecified, it will look for a process environment variable "
                                                         "FASTIOT_DOCKER_REGISTRY_CACHE. If docker registry cache is "
                                                         "not empty, it will use it as a cache for intermediate image "
                                                         "layers."),
          platform: str = typer.Option('', '-p', '--platform', shell_complete=_platform_completion,
                                       help="The platform to compile for given as a comma ',' separated list. Possible "
                                            "values are 'amd64' and 'arm64'. Currently, it is only supported in "
                                            "combination with the '--push' flag. Per default, the platform of the "
                                            "current OS is used. If multiple platforms are specified, they will be "
                                            "included into the resulting image.\n"
                                            "It will also look in the manifest.yaml and check if each service can be "
                                            "built for the selected platform. If not, the platform builds will be "
                                            "skipped where unspecified. If nothing can be built, it will exit with 2."),
          dry: bool = typer.Option(False, '-d', '--dry',
                                   help="Only generate necessary build files withouth executing them. Useful for "
                                        "debugging purposes."),
          push: bool = typer.Option(False, '--push',
                                    help="Instead of using --load for buildx, it uses --push which outputs the image "
                                         "to a registry. Push is only allowed if a docker registry is specified. "
                                         "Additionally, if a docker registry cache is used, it will also push "
                                         "intermediate image layers."),
          test_deployment_only: bool = typer.Option(False,
                                                    help="Build only services defined in the integration test "
                                                         "deployment. This is especially useful in the "
                                                         "CI-runner"),
          no_cache: bool = typer.Option(False, help="Force disabling caches for build.")):
    """
    This command builds images.

    Per default, it builds all images. Optionally, you can specify a single image to build.
    """
    logging.info("Starting build of project!")
    if docker_registry:
        logging.info("Using Docker registry %s to tag images", docker_registry)
    else:
        logging.info("Not using a docker registry for image tagging")

    # Workaround as currently (6/2022) an optional list will not result in None but in an empty tuple, which is nasty
    # to check
    if not services:
        services = None

    context = ProjectContext.default

    if test_deployment_only:
        if not context.integration_test_deployment:
            logging.error("No `integration_test_deployment` configured. Stopping to build.")
            raise typer.Exit(0)
        services = _find_test_deployment_services(context)

    _create_all_docker_files(context, services=services)
    tags = tag.split(',')
    _docker_bake(context, tags=tags, build_mode=mode, services=services, dry=dry, push=push,
                 docker_registry=docker_registry, docker_registry_cache=docker_registry_cache, platform=platform,
                 no_cache=no_cache)

    logging.info("Successfully built project. For reference you may consult the dockerfiles in your build directory.")


def _create_all_docker_files(context: ProjectContext, services: Optional[List[str]] = None):
    for service in context.services:
        if services is None or service.name in services:
            _create_docker_file(service, context)


def _create_docker_file(service: Service, context: ProjectContext):
    build_dir = os.path.join(context.project_root_dir, context.build_dir, DOCKER_BUILD_DIR)
    os.makedirs(build_dir, exist_ok=True)

    docker_filename = os.path.join(build_dir, 'Dockerfile.' + service.name)

    service_own_dockerfile = os.path.join(context.project_root_dir, 'src',
                                          service.package, service.name, 'Dockerfile')
    if os.path.isfile(service_own_dockerfile):
        logging.debug("Using dockerfile from %s, not creating a new one", service.name)
        copyfile(service_own_dockerfile, docker_filename)

    else:
        with open(docker_filename, "w") as dockerfile:
            manifest = service.read_manifest()
            template = DockerTemplate.get(manifest.template)
            dockerfile_template = get_jinja_env(template_dir=template.dir).get_template(template.filename)
            dockerfile.write(dockerfile_template.render(service=service,
                                                        manifest=manifest,
                                                        context=context,
                                                        extra_pypi=os.environ.get('FASTIOT_EXTRA_PYPI',
                                                                                  "www.piwheels.org/simple/"),
                                                        maintainer=_get_maintainer()
                                                        )
                             )


def _get_maintainer() -> str:

    cmd = "git show -q HEAD"
    try:
        git_log = subprocess.getoutput(cmd)
        author, mail = re.search("^Author: (.*) (<.*@.*>)$", git_log, re.MULTILINE).groups()
        maintainer = f"{author} using FastIoT {mail}"
    except (AttributeError, TypeError):
        maintainer = "FastIoT Framework <none@none>"

    return maintainer


def _docker_bake(context: ProjectContext,
                 tags: List[str],
                 build_mode: str,
                 services: Optional[List[str]] = None,
                 dry: bool = False,
                 platform: str = '',
                 docker_registry: str = '',
                 docker_registry_cache: str = '',
                 push: bool = False,
                 no_cache: bool = False):
    """ Method to create a :file:`docker-bake.hcl` file and invoke the docker bake command """

    class TargetConfiguration(BaseModel):
        manifest: ServiceManifest
        cache_from: str
        cache_to: str

    docker_registry = docker_registry + "/" if docker_registry else docker_registry

    targets = []
    for service in context.services:
        if services is not None and service.name not in services:
            continue
        manifest = service.read_manifest()

        if platform:  # Overwrite platform from manifest with manual setting
            if platform not in manifest.platforms:
                logging.warning("Platform %s not in platforms specified for service %s. Trying to build service, "
                                "but chances to fail are high!", platform, service.name)
            manifest.platforms = [CPUPlatform(platform)]
        elif not push:
            manifest.platforms = [manifest.platforms[0]]  # For local builds only one platform can be used. Using 1.

        if not no_cache:
            cache_from, cache_to = _make_caches(
                docker_registry_cache=docker_registry_cache,
                docker_cache_image=service.cache,
                extra_caches=service.extra_caches,
                push=push,
                tags=tags
            )
        else:
            cache_from, cache_to = '', ''

        targets.append(TargetConfiguration(manifest=manifest, cache_from=cache_from, cache_to=cache_to))

    if len(targets) == 0:
        if services is not None:
            logging.warning("Service(s) %s could not be found in project configuration, aborting build",
                            ", ".join(services))
        else:
            logging.warning("No services selected to build, aborting build of services.")
        logging.info("Configured and valid services for this project are: %s",
                     ", ".join([s.name for s in context.services]))
        raise typer.Exit()

    with open(os.path.join(context.project_root_dir, context.build_dir,
                           DOCKER_BUILD_DIR, 'docker-bake.hcl'), "w") as docker_bake_hcl:
        dockerfile_template = get_jinja_env().get_template('docker-bake.hcl.j2')
        docker_bake_hcl.write(dockerfile_template.render(targets=targets,
                                                         modes=BUILD_MODES,
                                                         project_config=context,
                                                         tags=tags,
                                                         docker_registry=docker_registry))

    if not dry:
        _run_docker_bake_cmd(context, build_mode, push, no_cache)


def _find_test_deployment_services(project_config: ProjectContext) -> List[str]:
    """ Builds a list of services based on the test env project configuration. May exit the program if no services are
    to be built."""
    if project_config.integration_test_deployment is None:
        logging.info("No services to build for test environment as no test environment is specified.")
        raise typer.Exit()
    deployment = project_config.deployment_by_name(project_config.integration_test_deployment)
    services = list(deployment.services.keys())
    if len(services) == 0:
        logging.info("No services to build if selecting only test environment.")
        raise typer.Exit()
    logging.info("Building services %s for testing", ", ".join(services))
    return services


def _run_docker_bake_cmd(project_config, build_mode, push, no_cache):
    # Prepare system for multi-arch builds
    os.environ['DOCKER_CLI_EXPERIMENTAL'] = 'enabled'
    os.environ['DOCKER_BUILDKIT'] = '1'
    qemu_platforms = {p.as_qemu_platform() for p in CPUPlatform}

    # We uninstall any registered qemu emulators first. Sometimes simply (re)-installing seems not to be enough and
    # will cause random segfaults especially when running apt within the ARM64-container
    for cmd in ['docker run --privileged --rm tonistiigi/binfmt --uninstall "qemu-*"',
                f"docker run --privileged --rm tonistiigi/binfmt --install {','.join(qemu_platforms)}",
                f"docker buildx create --name {BUILDER_NAME} --driver-opt image=moby/buildkit:master --use",
                "docker buildx inspect --bootstrap"]:
        subprocess.call(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    try:
        docker_cmd = f"docker buildx bake -f {project_config.build_dir}/{DOCKER_BUILD_DIR}/docker-bake.hcl"
        if push:
            docker_cmd += " --push"
        else:
            docker_cmd += " --load"
        if no_cache:
            docker_cmd += " --no-cache"
        # set target group
        docker_cmd += f" {build_mode}"
        exit_code = subprocess.call(f"{docker_cmd}".split(), cwd=project_config.project_root_dir)
        if exit_code != 0:
            logging.error("docker buildx bake failed with exit code %s.", str(exit_code))
            raise typer.Exit(exit_code)
    finally:
        if not env_cli.is_ci_runner:  # Stop and remove the buildkit container
            docker_cmd_stop_builder = ["docker", "buildx", "stop", BUILDER_NAME]
            docker_cmd_rm_builder = ["docker", "buildx", "rm", BUILDER_NAME]
            subprocess.call(docker_cmd_stop_builder, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            subprocess.call(docker_cmd_rm_builder, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def _make_caches(docker_registry_cache: str,
                 docker_cache_image: str,
                 extra_caches: List[str],
                 push: bool,
                 tags: List[str]):
    project_namespace = ProjectContext.default.project_namespace
    caches_from = []

    # Sort the tags: If we have a `latest` we want this to be first for the push the cache.
    if 'latest' in tags:
        tags = ['latest'] + [t for t in tags if t != 'latest']

    if docker_registry_cache:
        for tag in tags:
            caches_from.append(
                f'"type=registry,ref={docker_registry_cache}/{project_namespace}/{docker_cache_image}:{tag}"'
            )
        if extra_caches:
            for cache in extra_caches:
                caches_from.append(f'"type=registry,ref={docker_registry_cache}/{cache}"')
    local_cache = os.path.join(ProjectContext.default.project_root_dir, '.docker-cache')
    if os.path.isdir(local_cache) and not push:
        # If local cache is found we add it. Please not that this might get ignored if option --no-cache is used.
        # That's why this log message is quite generic to not confuse the user.
        logging.info("Local cache available.")
        caches_from.append(f'"type=local,src={local_cache}"')
    else:
        logging.info("Currently no local cache available.")

    if push and docker_registry_cache:
        cache_to = f'"type=registry,ref={docker_registry_cache}/{project_namespace}/' \
                   f'{docker_cache_image}:{tags[0]},mode=max"'
    elif not push:
        cache_to = f'"type=local,dest={local_cache},mode=max"'
    else:
        cache_to = ""

    cache_from = ",\n                  ".join(caches_from)
    return cache_from, cache_to
