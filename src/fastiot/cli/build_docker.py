import os.path

from fastiot.cli.configuration.constants import assets_dir
from fastiot.cli.helper_fn import get_jinja_env, find_modules
from fastiot.cli.model import ProjectConfiguration, ModuleManifest


def build_overall_project(project_config: ProjectConfiguration):
    create_all_docker_files(project_config)
    docker_bake(project_config)


def create_all_docker_files(project_config: ProjectConfiguration):
    for module_package in project_config.module_packages:
        if module_package.module_names is None:
            module_package.module_names = find_modules(module_package.package_name, project_config.project_root_dir)
        for module_name in module_package.module_names:
            create_docker_file(module_package.package_name, module_name, project_config)


def create_docker_file(module_package_name: str, module_name: str, project_config: ProjectConfiguration):
    build_dir = os.path.join(project_config.project_root_dir, 'build')
    try:
        os.mkdir(build_dir)
    except FileExistsError:
        pass  # No need to create directory twice

    docker_filename = os.path.join(build_dir, 'Dockerfile.' + module_name)
    manifest_path = os.path.join(project_config.project_root_dir, 'src', module_package_name, module_name,
                                 'manifest.yaml')
    manifest = ModuleManifest.from_yaml_file(manifest_path, check_module_name=module_name)

    with open(docker_filename, "w") as dockerfile:
        dockerfile_template = get_jinja_env(search_path=assets_dir).get_template('Dockerfile.jinja')
        dockerfile.write(dockerfile_template.render(module_package_name=module_package_name,
                                                    module_name=module_name,
                                                    project_config=project_config,
                                                    manifest=manifest,
                                                    extra_pypi=os.environ.get('FASTIOT_EXTRA_PYPI',
                                                                              "www.piwheels.org/simple/")))


def docker_bake(project_config: ProjectConfiguration):
    """ Method to create a :file:`docker-bake.hcl` file and invoke the docker bake command"""
    pass  # TODO: This is still a stub


if __name__ == '__main__':
    from fastiot.cli.import_configure import import_configure

    project_configuration = import_configure()
    create_all_docker_files(project_configuration)
