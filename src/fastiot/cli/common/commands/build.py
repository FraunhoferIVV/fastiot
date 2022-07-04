import logging
import os.path
import subprocess
from enum import Enum
from typing import List, Optional

import typer
from pydantic.main import BaseModel

from fastiot.cli.constants import FASTIOT_DOCKER_REGISTRY, FASTIOT_DOCKER_REGISTRY_CACHE
from fastiot.cli.helper_fn import get_jinja_env
from fastiot.cli.model import ProjectConfig, ServiceManifest
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import app, DEFAULT_CONTEXT_SETTINGS


class Mode(str, Enum):
    debug = 'debug'
    release = 'release'


def _get_services_enum():
    default_context = get_default_context()
    services_dict = {
        service: service for service in default_context.project_config.services
    }
    return Enum('Services', services_dict)


Modules = _get_services_enum()


@app.command(context_settings=DEFAULT_CONTEXT_SETTINGS)
def build(modules: List[Modules] = typer.Argument(None, help="The modules to build. Default: all modules"),
          mode: Mode = typer.Option(Mode.debug.value, '-m', '--mode',
                                    help="The build mode for docker images. "
                                         "No compilation of python code will happen if chosen 'debug'. Nuitka "
                                         "compilation will be applied if chosen 'release'."),
          tag: str = typer.Option('latest', '-t', '--tag',
                                  help="The tags to use for building as a comma ',' separated list."),
          docker_registry: str = typer.Option(None, '-r', '--docker_registry',
                                              envvar=FASTIOT_DOCKER_REGISTRY,
                                              help="The docker registry to be used for tagging. If docker_registry is "
                                                   "unspecified, it will look for a process environment variable "
                                                   "SAM_DOCKER_REGISTRY. If docker registry is not empty, the built "
                                                   "image names will begin with the docker registry followed by a "
                                                   "slash."),
          docker_registry_cache: str = typer.Option(None, '-c', '--docker_registry_cache',
                                                    envvar=FASTIOT_DOCKER_REGISTRY_CACHE,
                                                    help="The docker registry cache. If docker registry cache is "
                                                         "unspecified, it will look for a process environment variable "
                                                         "SAM_DOCKER_REGISTRY_CACHE. If docker registry cache is not "
                                                         "empty, it will use it as a cache for intermediate image "
                                                         "layers."),
          platform: str = typer.Option(None, '-p', '--platform',
                                       help="The platform to compile for given as a comma ',' separated list. Possible "
                                            "values are 'amd64', 'arm64', 'armv6' and 'armv7'. Currently, it is only "
                                            "supported in combination with the '--push' flag. Per default, the "
                                            "platform of the current OS is used. If multiple platforms are specified, "
                                            "they will be included into the resulting image. \n"
                                            "It will also look in the manifest.yaml and check if each module can be "
                                            "built for the selected platform. If not, the platform builds will be "
                                            "skipped where unspecified. If nothing can be built, it will exit with 2."),
          dry: bool = typer.Option(False, '-d', '--dry',
                                   help="Only generate necessary build files withouth executing them. Useful for "
                                        "debugging purposes."),
          push: bool = typer.Option(False, '--push',
                                    help="Instead of using --load for buildx, it uses --push which outputs the image "
                                         "to a registry. Push is only allowed if a docker registry is specified. "
                                         "Additionally, if a docker registry cache is used, it will also push "
                                         "intermediate image layers.")
          ):
    """
    This command builds images.

    Per default it builds all images. Optionally, you can specify a single image to build.

    If you want to use experimental features like platform tag, use the flag -e to indicate it.
    """
    logging.info(f"Docker registry: {docker_registry}")
    os.system("export DOCKER_CLI_EXPERIMENTAL=enabled; "
              "docker run --rm --privileged docker/binfmt:a7996909642ee92942dcd6cff44b9b95f08dad64; "
              "docker buildx create --name fastiot_builder --driver-opt image=moby/buildkit:master --use; "
              "docker buildx inspect --bootstrap; ")

    project_config = get_default_context().project_config
    create_all_docker_files(project_config, build_mode=mode, modules=modules)
    tags = tag.split(',')
    docker_bake(project_config, tags=tags, modules=modules, dry=dry, push=push, docker_registry=docker_registry,
                docker_registry_cache=docker_registry_cache, platform=platform)


def create_all_docker_files(project_config: ProjectConfig, build_mode: str, modules: Optional[List[str]] = None):
    for module_package in project_config.module_packages:
        for module_name in module_package.module_names:
            if modules is None or module_name in modules:
                create_docker_file(module_package.package_name, module_name, project_config, build_mode)


def create_docker_file(module_package_name: str, module_name: str, project_config: ProjectConfig,
                       build_mode: str):
    build_dir = os.path.join(project_config.project_root_dir, project_config.build_dir)
    try:
        os.mkdir(build_dir)
    except FileExistsError:
        pass  # No need to create directory twice

    docker_filename = os.path.join(build_dir, 'Dockerfile.' + module_name)
    manifest_path = _get_manifest_path(module_name, module_package_name, project_config)
    manifest = ServiceManifest.from_yaml_file(manifest_path, check_service_name=module_name)

    with open(docker_filename, "w") as dockerfile:
        dockerfile_template = get_jinja_env().get_template('Dockerfile.jinja')
        dockerfile.write(dockerfile_template.render(module_package_name=module_package_name,
                                                    project_config=project_config,
                                                    manifest=manifest,
                                                    extra_pypi=os.environ.get('FASTIOT_EXTRA_PYPI',
                                                                              "www.piwheels.org/simple/"),
                                                    build_mode=build_mode))


def docker_bake(project_config: ProjectConfig,
                tags: List[str],
                modules: Optional[List[str]] = None,
                dry: bool = False,
                platform: Optional[str] = None,
                docker_registry: Optional[str] = None,
                docker_registry_cache: Optional[str] = None,
                push: bool = False):
    """ Method to create a :file:`docker-bake.hcl` file and invoke the docker bake command """

    class TargetConfiguration(BaseModel):
        manifest: ServiceManifest
        cache_from: str
        cache_to: str

    if docker_registry is None:
        docker_registry = os.environ.get('FASTIOT_DOCKER_REGISTRY', "")
    docker_registry = docker_registry + "/" if docker_registry != "" else docker_registry

    if docker_registry_cache is None:
        docker_registry_cache = os.environ.get('FASTIOT_DOCKER_REGISTRY_CACHE')

    targets = list()
    for module_package in project_config.module_packages:
        module_package.cache_name = module_package.cache_name or f"{project_config.project_namespace}:latest"
        for module_name in module_package.module_names:
            if modules is not None and module_name not in modules:
                continue
            manifest_path = _get_manifest_path(module_name, module_package.package_name, project_config)
            manifest = ServiceManifest.from_yaml_file(manifest_path)
            if platform is not None:  # Overwrite platform from manifest with manual setting
                if platform not in manifest.platforms:
                    logging.warning("Platform %s not in platforms specified for module %s. Trying to build module, "
                                    "but chances to fail are high!", platform, module_name)
                manifest.platforms = platform
            elif not push:
                manifest.platforms = [manifest.platforms[0]]  # For local builds only one platform can be used. Using 1.
            if manifest.docker_cache_image is None:  # Set cache from module level if not defined otherwise
                manifest.docker_cache_image = module_package.cache_name

            cache_from, cache_to = _set_caches(docker_registry_cache, manifest.docker_cache_image,
                                               module_package.extra_caches, push)

            targets.append(TargetConfiguration(manifest=manifest, cache_from=cache_from, cache_to=cache_to))

    if not os.path.exists(os.path.join(project_config.project_root_dir, project_config.build_dir)):
        os.mkdir(os.path.join(project_config.project_root_dir, project_config.build_dir))

    with open(os.path.join(project_config.project_root_dir, project_config.build_dir, 'docker-bake.hcl'),
              "w") as docker_bake_hcl:
        dockerfile_template = get_jinja_env().get_template('docker-bake.hcl.jinja')
        docker_bake_hcl.write(dockerfile_template.render(targets=targets,
                                                         project_config=project_config,
                                                         tags=tags,
                                                         docker_registry=docker_registry))

    if not dry:
        docker_cmd = f"docker buildx bake -f {project_config.build_dir}/docker-bake.hcl"
        if push:
            docker_cmd += " --push"
        else:
            docker_cmd += " --load"
        exit_code = subprocess.call(f"{docker_cmd}".split(), cwd=project_config.project_root_dir)
        if exit_code != 0:
            raise RuntimeError("docker buildx bake failed with exit code " + str(exit_code))


def _get_manifest_path(module_name: str, module_package_name: str, project_config: ProjectConfig):
    manifest_path = os.path.join(project_config.project_root_dir, 'src', module_package_name, module_name,
                                 'manifest.yaml')
    return manifest_path


def _set_caches(docker_registry_cache, docker_cache_image, extra_caches, push: bool):
    caches_from = list()
    if docker_registry_cache is not None:
        caches_from.append(f'"type=registry,src={docker_registry_cache}/{docker_cache_image}"')
        if extra_caches is not None:
            for cache in extra_caches:
                caches_from.append(f'"type=registry,src={docker_registry_cache}/{cache}"')
    if push is not None:  # We are most probably in a local environment, so try to use this cache as well
        caches_from.append('"type=local,src=.docker-cache"')

    if push and docker_registry_cache is not None:
        cache_to = f'"type=registry,dst={docker_registry_cache}/{docker_cache_image}"'
    elif not push:
        cache_to = '"type=local,dest=.docker-cache"'
    else:
        cache_to = ""

    cache_from = ",\n".join(caches_from)
    return cache_from, cache_to
