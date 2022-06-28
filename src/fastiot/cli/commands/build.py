""" Build command """
import importlib
import logging
import os.path
import subprocess
import sys
from glob import glob
from typing import List, Optional

import typer
from pydantic import BaseModel

from fastiot.cli.constants import FASTIOT_DOCKER_REGISTRY, FASTIOT_DOCKER_REGISTRY_CACHE
from fastiot.cli.helper_fn import get_jinja_env
from fastiot.cli.model import ProjectConfig, ModuleManifest, CPUPlatform, ModuleConfig
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import app, DEFAULT_CONTEXT_SETTINGS


def _mode_completion() -> List[str]:
    return ['debug', 'release']


def _mode_callback(mode: str):
    if mode not in _mode_completion():
        raise typer.BadParameter(f"Mode must be 'debug' or 'release'. But it is {mode}")
    return mode


def _modules_completion() -> List[str]:
    return [os.path.basename(os.path.dirname(m)) for m in list(glob("src/*/*/manifest.yaml"))]


def _platform_completion() -> List[str]:
    return [p.value for p in CPUPlatform]


@app.command(context_settings=DEFAULT_CONTEXT_SETTINGS)
def build(mode: str = typer.Option('debug', '-m', '--mode',
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
                                                         "FASTIOT_DOCKER_REGISTRY_CACHE. If docker registry cache is not "
                                                         "empty, it will use it as a cache for intermediate image "
                                                         "layers."),
          platform: str = typer.Option(None, '-p', '--platform', shell_complete=_platform_completion,
                                       help="The platform to compile for given as a comma ',' separated list. Possible "
                                            "values are 'amd64' and 'arm64'. Currently, it is only supported in "
                                            "combination with the '--push' flag. Per default, the platform of the "
                                            "current OS is used. If multiple platforms are specified, they will be "
                                            "included into the resulting image.\n"
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
                                         "intermediate image layers."),
          test_env_only: Optional[bool] = typer.Option(False,
                                                       help="Build only modules defined in the test environment. "
                                                            "This is especially useful in the CI-runner"),
          no_cache: Optional[bool] = typer.Option(False, help="Force disabling caches for build."),
          modules: Optional[List[str]] = typer.Argument(None, help="The modules to build. Default: all modules",
                                                        shell_complete=_modules_completion)
          ):
    """
    This command builds images.

    Per default, it builds all images. Optionally, you can specify a single image to build.
    """
    logging.info("Using Docker registry: %s", docker_registry)

    # Workaround as currently (6/2022) an optional list will not result in None but in an empty tuple, which is nasty
    # to check
    if not modules:
        modules = None

    project_config = get_default_context().project_config

    if test_env_only:
        modules = _find_test_env_modules(project_config)

    _create_all_docker_files(project_config, build_mode=mode, modules=modules)
    tags = tag.split(',')
    _docker_bake(project_config, tags=tags, modules=modules, dry=dry, push=push, docker_registry=docker_registry,
                 docker_registry_cache=docker_registry_cache, platform=platform, no_cache=no_cache)


def _create_all_docker_files(project_config: ProjectConfig, build_mode: str, modules: Optional[List[str]] = None):
    for module in project_config.modules:
        if modules is None or module.name in modules:
            module.read_manifest()
            _create_docker_file(module, project_config, build_mode)


def _create_docker_file(module: ModuleConfig, project_config: ProjectConfig, build_mode: str):
    build_dir = os.path.join(project_config.project_root_dir, project_config.build_dir)
    os.makedirs(build_dir, exist_ok=True)

    docker_filename = os.path.join(build_dir, 'Dockerfile.' + module.name)

    with open(docker_filename, "w") as dockerfile:
        dockerfile_template = get_jinja_env().get_template('Dockerfile.jinja')
        dockerfile.write(dockerfile_template.render(module=module,
                                                    project_config=project_config,
                                                    extra_pypi=os.environ.get('FASTIOT_EXTRA_PYPI',
                                                                              "www.piwheels.org/simple/"),
                                                    build_mode=build_mode))


def _docker_bake(project_config: ProjectConfig,
                 tags: List[str],
                 modules: Optional[List[str]] = None,
                 dry: bool = False,
                 platform: Optional[str] = None,
                 docker_registry: Optional[str] = None,
                 docker_registry_cache: Optional[str] = None,
                 push: bool = False,
                 no_cache: bool = False):
    """ Method to create a :file:`docker-bake.hcl` file and invoke the docker bake command """

    class TargetConfiguration(BaseModel):
        manifest: ModuleManifest
        cache_from: str
        cache_to: str

    docker_registry = docker_registry + "/" if docker_registry != "" else docker_registry

    targets = []
    for module in project_config.modules:
        if modules is not None and module.name not in modules:
            continue
        manifest = module.read_manifest()

        if platform is not None:  # Overwrite platform from manifest with manual setting
            if platform not in manifest.platforms:
                logging.warning("Platform %s not in platforms specified for module %s. Trying to build module, "
                                "but chances to fail are high!", platform, module.name)
            manifest.platforms = [CPUPlatform(platform)]
        elif not push:
            manifest.platforms = [manifest.platforms[0]]  # For local builds only one platform can be used. Using 1.
        if manifest.docker_cache_image is None:  # Set cache from module level if not defined otherwise
            manifest.docker_cache_image = module.cache

        cache_from, cache_to = _set_caches(docker_registry_cache, manifest.docker_cache_image,
                                           module.extra_caches, push)

        targets.append(TargetConfiguration(manifest=manifest, cache_from=cache_from, cache_to=cache_to))

    if len(targets) == 0:
        logging.warning("No modules selected to build, aborting build of modules.")
        raise typer.Exit()

    with open(os.path.join(project_config.project_root_dir, project_config.build_dir, 'docker-bake.hcl'),
              "w") as docker_bake_hcl:
        dockerfile_template = get_jinja_env().get_template('docker-bake.hcl.jinja')
        docker_bake_hcl.write(dockerfile_template.render(targets=targets,
                                                         project_config=project_config,
                                                         tags=tags,
                                                         docker_registry=docker_registry))

    if not dry:
        _run_docker_bake_cmd(project_config, push, no_cache)


def _find_test_env_modules(project_config: ProjectConfig) -> List[str]:
    """ Builds a list of modules based on the test env project configuration. May exit the program if no modules are to
    be built."""
    if project_config.test_config is None:
        logging.info("No modules to build for test environment as no test environment is specified.")
        raise typer.Exit()
    deployment = project_config.get_deployment_by_name(project_config.test_config)
    modules = list(deployment.modules.keys())
    if len(modules) == 0:
        logging.info("No modules to build if selecting only test environment.")
        raise typer.Exit()
    logging.info("Building modules %s for testing", ", ".join(modules))
    return modules


def _run_docker_bake_cmd(project_config, push, no_cache):

    # Prepare system for multi-arch builds
    os.system("export DOCKER_CLI_EXPERIMENTAL=enabled; "
              "docker run --rm --privileged multiarch/qemu-user-static --reset -p yes; "
              "docker buildx create --name fastiot_builder --driver-opt image=moby/buildkit:master --use; "
              "docker buildx inspect --bootstrap; ")

    docker_cmd = f"docker buildx bake -f {project_config.build_dir}/docker-bake.hcl"
    if push:
        docker_cmd += " --push"
    else:
        docker_cmd += " --load"
    if no_cache:
        docker_cmd += " --no-cache"
    exit_code = subprocess.call(f"{docker_cmd}".split(), cwd=project_config.project_root_dir)
    if exit_code != 0:
        logging.error("docker buildx bake failed with exit code %s", str(exit_code))
        if not no_cache:
            docker_cmd += " --no-cache"
            exit_code = subprocess.call(f"{docker_cmd}".split(), cwd=project_config.project_root_dir)
            sys.exit(exit_code)


def _set_caches(docker_registry_cache, docker_cache_image, extra_caches, push: bool):
    caches_from = []
    if docker_registry_cache is not None:
        caches_from.append(f'"type=registry,ref={docker_registry_cache}/{docker_cache_image}"')
        if extra_caches is not None:
            for cache in extra_caches:
                caches_from.append(f'"type=registry,src={docker_registry_cache}/{cache}"')
    if not push:  # We are most probably in a local environment, so try to use this cache as well
        caches_from.append('"type=local,src=.docker-cache"')

    if push and docker_registry_cache is not None:
        cache_to = f'"type=registry,mode=max,ref={docker_registry_cache}/{docker_cache_image}"'
    elif not push:
        cache_to = '"type=local,dest=.docker-cache,mode="max""'
    else:
        cache_to = ""

    cache_from = ",\n                  ".join(caches_from)
    return cache_from, cache_to