"""
Commands for generating new projects and services.
"""
import logging
import os
import shutil
from typing import Optional

import typer

from fastiot import get_version
from fastiot.cli.constants import FASTIOT_CONFIGURE_FILE
from fastiot.cli.helper_fn import get_jinja_env
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import create_cmd


@create_cmd.command()
def new_project(project_name: str = typer.Argument(None, help="The project name to generate"),
                force: Optional[bool] = typer.Option(False, '-f', '--force',
                                                     help="Create project even if an existing project has been found."),
                target_directory: Optional[str] = typer.Option('.', '-d', '--directory',
                                                               help="The directory the project will be stored")
                ):
    """
    Function to create a new project with its directory structure and all needed files for a quick start.

    You may use the function `new-service` afterwards to create your first service stubs.
    """
    os.environ[FASTIOT_CONFIGURE_FILE] = os.path.join(target_directory, 'configure.py')
    project_config = get_default_context().project_config
    if project_config.project_namespace != "" and not force:
        logging.error("An existing project configuration has been found with project namespace %s. "
                      "To force overwriting this you may use the --force argument.",
                      get_default_context().project_config.project_namespace)
        raise typer.Exit(2)

    if target_directory.startswith('/'):
        project_config.project_root_dir = target_directory
    else:
        project_config.project_root_dir = os.path.join(project_config.project_root_dir, target_directory)


    # TODO: Check for valid project name (no space, no /, …)
    not_usable: bool = True

    project_name = project_name.replace(" ", "_").replace("-", '_')
    for letter in project_name:
        if letter.isalnum() or letter == "_" or letter == ".":
            not_usable = False
        else:
            not_usable = True
            break
    if not_usable:
        logging.error("Please enter valid Name. Only use a-z, A-Z, 0-9, '.' and '_' .")
        raise typer.Exit(3)

    # TODO: Create necessary directories
    if not os.path.exists(project_config.project_root_dir):
        os.makedirs(project_config.project_root_dir)
    for directory in [f"{project_name}_lib", f"{project_name}_tests", f"{project_name}_services"]:
        if not os.path.exists(directory):
            os.makedirs(os.path.join(project_config.project_root_dir, directory))

    # TODO: Loop over many templates used to create a new project
    with open(os.path.join(project_config.project_root_dir, 'configure.py'), "w") as docker_compose_file:
        configure_py_template = get_jinja_env().get_template('new_project/configure.py.j2')
        docker_compose_file.write(configure_py_template.render(
            project_namespace=project_name,
        ))

    with open(os.path.join(project_config.project_root_dir, 'requirements.txt'), "w") as docker_compose_file:
        configure_py_template = get_jinja_env().get_template('new_project/requirements.txt.j2')
        docker_compose_file.write(configure_py_template.render(
            project_namespace=project_name,
            version=get_version(),
            major_version=int(get_version(False, True, False))
        ))

    # TODO: Copy static files like .gitignore
    templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'new_project')
    for src, dest in [('.dockerignore', '.'),
                      ('.gitignore', '.'),
                      ('install.sh', '.')]:
        shutil.copy(os.path.join(templates_dir, src), os.path.join(project_config.project_root_dir, dest))

    shutil.copytree(os.path.join(project_config.project_root_dir, 'deployments/integration_test'),
                    os.path.join(project_config.project_root_dir, 'deployments/integration_test'))

    # shutil.copytree(os.path.join(project_config.project_root_dir, 'src/fastiot/cli/templates/new_project/.run'),
                    # os.path.join(project_config.project_root_dir, '.run'))

    logging.warning("This method has not yet been fully implemented")

@create_cmd.command()
def new_service(service_name: str = typer.Argument(None, help="The service name to generate"),
                service_package: Optional[str] = typer.Option(default=None, help="Specify the package to create the "
                                                                                 "service in. If left empty the first "
                                                                                 "package configured will be used.")):
    not_usable: bool = True
    service_name = service_name.replace(" ", "_").replace("-", '_')
    for letter in service_name:
        if (letter.isalnum() and letter.islower()) or letter == "_" or letter == ".":
            not_usable = False
        else:
            not_usable = True
            break
    if not_usable:
        logging.error("Please enter valid Name. Only use a-z, 0-9, '.' and '_' .")
        exit()

    if service_package is None:
        service_package = '/home/sieber/PycharmProjects/fastiot'

    service_location = os.path.join(service_package, service_name)
    os.mkdir(service_location)

    # Templates
    # Manifest
    with open(os.path.join(service_location, 'manifest.ymal'), "w") as file:
        configure_py_template = get_jinja_env().get_template('new_service/manifest.yaml.j2')
        file.write(configure_py_template.render(
            service_name=service_name,
        ))


    #__init__.py
    open(os.path.join(service_location,"__init__.py"),"w")
    # servicename_service datei.py
    with open(os.path.join(service_location, f'{service_name}_service.py'), "w") as file:
        configure_py_template = get_jinja_env().get_template('new_service/servicename_service.py.j2')
        file.write(configure_py_template.render(
            service_name=service_name,
            service_name_camel=service_name.capitalize()
        ))

    # .run
    with open(os.path.join(service_location, 'run.py'), "w") as file:
        configure_py_template = get_jinja_env().get_template('new_service/.run.py.j2')
        file.write(configure_py_template.render(
            service_name=service_name,
            service_name_camel=service_name.capitalize()
        ))


    logging.error("This method has not yet been implemented")
    raise typer.Exit(1)
