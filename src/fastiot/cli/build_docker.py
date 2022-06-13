import os.path
import subprocess
from typing import List, Optional

from fastiot.cli.configuration.constants import assets_dir
from fastiot.cli.helper_fn import get_jinja_env, find_modules
from fastiot.cli.import_configure import import_configure
from fastiot.cli.model import ProjectConfiguration, ModuleManifest


def build_overall_project(build_mode: str = 'debug',
                          tags: Optional[List[str]] = None,
                          modules: Optional[List[str]] = None):

    project_config = import_configure()
    create_all_docker_files(project_config, build_mode=build_mode, modules=modules)
    tags = tags or ['latest']
    docker_bake(project_config, tags=tags, modules=modules)


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


def docker_bake(project_config: ProjectConfiguration, tags: List[str], modules: Optional[List[str]] = None):
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
