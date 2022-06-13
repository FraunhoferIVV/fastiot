import os.path
import subprocess
from typing import List, Optional

from fastiot.cli.configuration.constants import assets_dir
from fastiot.cli.helper_fn import get_jinja_env, find_modules
from fastiot.cli.import_configure import import_configure
from fastiot.cli.model import ProjectConfiguration, ModuleManifest


def build_overall_project(mode: str = 'debug',
                          tags: Optional[List[str]] = None,
                          docker_registry: Optional[str] = None,
                          docker_registry_cache: Optional[str] = None,
                          platform: Optional[str] = None,
                          push: bool = False,
                          dry: bool = True,
                          modules: Optional[List[str]] = None):
    """
    Usage: fastapi.cli build [<options>] [<module>]

    This command builds docker images. You must set an environment variable FASTAPI_EXTRA_PYPI to indicate where to find
    libraries.

    Per default it builds all modules. Optionally, you can specify a module to built only a single module.

    If you want to use experimental features like platform tag, use buildx instead of build.

    Options:

     -m <mode>, --mode=<mode>   The build mode for docker images. Can be 'debug' (default) or 'release'. No compilation
                                of python code will happen if chosen 'debug'. Nuitka compilation will be applied if
                                chosen 'release'.
     -t <list(tag1,tag2,...,tagn)>, --tag=<list(tag1,tag2,...,tagn)>
                                The tags to use for building as a comma ',' separated list. Defaults to 'latest'.
     -r <docker_registry>, --docker_registry=<docker_registry>
                                The docker registry to be used for tagging. If docker_registry is unspecified, it will look
                                for a process environment variable FASTAPI_DOCKER_REGISTRY. If docker registry is not empty,
                                the built image names will begin with the docker registry followed by a slash.
     -c <docker_registry_cache>, --docker_registry_cache=<docker_registry_cache>
                                The docker registry cache. If docker registry cache is unspecified it will look for a
                                process environment variable FASTAPI_DOCKER_REGISTRY_CACHE.
                                If docker registry cache is not empty, it will use it as a cache for intermediate image
                                layers.
     -p <list(amd64,arm64)>, --platform=<list(amd64,arm64)>
                                The platform to compile for given as a comma ',' separated list.
                                Possible values are 'amd64' and 'arm64'. Currently, it is only supported
                                in combination with the '--push' flag. Per default, the platform of the current OS
                                is used. If multiple platforms are specified, they will be included into the resulting
                                image.
                                It will also look in the manifest.yaml and check if each module can be built for the
                                selected platform. If not, the platform builds will be skipped where unspecified. If nothing
                                can be built, it will exit with 2.
     --push                     Instead of using --load for `docker buildx`, it uses --push which outputs the
                                image to a registry. Push is only allowed if a docker registry is specified. Additionally,
                                if a docker registry cache is used, it will also push intermediate image layers.
     -d, --dry                  Instead of building, the cli will just create the dockerfiles and a docker-bake.hcl file
     -h, --help                 Print help
    """

    project_config = import_configure()
    create_all_docker_files(project_config, build_mode=mode, modules=modules)
    tags = tags or ['latest']
    docker_bake(project_config, tags=tags, modules=modules, dry=dry, push=push, docker_registry=docker_registry,
                          docker_registry_cache = docker_registry_cache, platform = platform)


def create_all_docker_files(project_config: ProjectConfiguration, build_mode: str, modules: Optional[List[str]] = None):
    for module_package in project_config.module_packages:
        if module_package.module_names is None:
            module_package.module_names = find_modules(module_package.package_name, project_config.project_root_dir)
        for module_name in module_package.module_names:
            if modules is None or module_name in modules:
                create_docker_file(module_package.package_name, module_name, project_config, build_mode)


def create_docker_file(module_package_name: str, module_name: str, project_config: ProjectConfiguration,
                       build_mode: str):
    build_dir = os.path.join(project_config.project_root_dir, 'build')
    try:
        os.mkdir(build_dir)
    except FileExistsError:
        pass  # No need to create directory twice

    docker_filename = os.path.join(build_dir, 'Dockerfile.' + module_name)
    manifest_path = _get_manifest_path(module_name, module_package_name, project_config)
    manifest = ModuleManifest.from_yaml_file(manifest_path, check_module_name=module_name)

    with open(docker_filename, "w") as dockerfile:
        dockerfile_template = get_jinja_env(search_path=assets_dir).get_template('Dockerfile.jinja')
        dockerfile.write(dockerfile_template.render(module_package_name=module_package_name,
                                                    project_config=project_config,
                                                    manifest=manifest,
                                                    extra_pypi=os.environ.get('FASTIOT_EXTRA_PYPI',
                                                                              "www.piwheels.org/simple/"),
                                                    build_mode=build_mode))


def docker_bake(project_config: ProjectConfiguration, tags: List[str], modules: Optional[List[str]] = None,
                dry: bool = False, platform: Optional[str] = None,
                docker_registry: Optional[str] = None, docker_registry_cache: Optional[str] = None,
                push: bool=False):
    """ Method to create a :file:`docker-bake.hcl` file and invoke the docker bake command """

    manifests = list()
    for module_package in project_config.module_packages:
        if module_package.module_names is None:
            module_package.module_names = find_modules(module_package.package_name, project_config.project_root_dir)
        for module_name in module_package.module_names:
            if modules is None or module_name in modules:
                manifest_path = _get_manifest_path(module_name, module_package.package_name, project_config)
                manifests.append(ModuleManifest.from_yaml_file(manifest_path))

    docker_registry = os.environ.get('FASTIOT_DOCKER_REGISTRY', "")
    docker_registry = docker_registry + "/" if docker_registry != "" else docker_registry

    with open(os.path.join(project_config.project_root_dir, 'build', 'docker-bake.hcl'), "w") as docker_bake_hcl:
        dockerfile_template = get_jinja_env(search_path=assets_dir).get_template('docker-bake.hcl.jinja')
        docker_bake_hcl.write(dockerfile_template.render(manifests=manifests,
                                                         project_config=project_config,
                                                         tags=tags,
                                                         docker_registry=docker_registry))

    if not dry:
        docker_cmd = f"docker buildx bake -f build/docker-bake.hcl"
        exit_code = subprocess.call(f"{docker_cmd}".split(), cwd=project_config.project_root_dir)
        if exit_code != 0:
            raise RuntimeError("docker buildx bake failed with exit code " + str(exit_code))


def _get_manifest_path(module_name: str, module_package_name: str, project_config: ProjectConfiguration):
    manifest_path = os.path.join(project_config.project_root_dir, 'src', module_package_name, module_name,
                                 'manifest.yaml')
    return manifest_path


if __name__ == '__main__':
    build_overall_project()
