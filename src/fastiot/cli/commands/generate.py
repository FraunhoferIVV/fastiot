"""
Commands for generating new projects and services.
"""
import logging
import os
import random
import shutil
import string
from typing import Optional

import typer

from fastiot.__version__ import __version__
from fastiot.cli.constants import DEPLOYMENTS_CONFIG_DIR, CONFIGURE_FILE_NAME, MANIFEST_FILENAME
from fastiot.cli.helper_fn import get_jinja_env
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import create_cmd


def _create_random_password(length: int) -> str:
    charlist = list(string.ascii_letters + string.digits + "_-.,:%&$?!*()")
    password: str = ""
    while len(password) < length:
        i: int = int(random.random()*100)
        while len(charlist) - 1 < i:
            i = i - len(charlist) - 2
        password = password + charlist[i]
    return password


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

    if os.path.isfile(os.path.join(target_directory, CONFIGURE_FILE_NAME)) and not force:
        logging.error("An existing project configuration has been found! "
                      "To force overwriting this you may use the --force argument.")
        raise typer.Exit(2)

    project_config = get_default_context().project_config

    if target_directory.startswith('/'):
        project_config.project_root_dir = target_directory
    else:
        project_config.project_root_dir = os.path.join(project_config.project_root_dir, target_directory)

    # Check for valid project name (no space, no /, …)
    project_name = project_name.replace(" ", "_").replace("-", '_')
    for letter in project_name:
        if not (letter.isalnum() or letter == "_" or letter == "."):
            logging.error("Please enter valid Name. Only use a-z, A-Z, 0-9, '.' and '_' .")
            raise typer.Exit(3)
    logging.info("The project %s will be created in %s", project_name, project_config.project_root_dir)

    # Create necessary directories
    if not os.path.exists(project_config.project_root_dir):
        os.makedirs(project_config.project_root_dir)
    for directory in [
                      os.path.join(DEPLOYMENTS_CONFIG_DIR, "integration_test"),
                      os.path.join("src", f"{project_name}_lib"),
                      os.path.join("src", f"{project_name}_tests"),
                      os.path.join("src", f"{project_name}_services")]:
        os.makedirs(os.path.join(project_config.project_root_dir, directory), exist_ok=True)

    # Copy static files like .gitignore
    templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'new_project')
    for src, dest in [('.dockerignore', '.'),
                      ('.gitignore', '.'),
                      ('install.sh', '.'),
                      ('deployment.yaml', os.path.join(DEPLOYMENTS_CONFIG_DIR, 'integration_test'))]:
        shutil.copy(os.path.join(templates_dir, src), os.path.join(project_config.project_root_dir, dest))

    # Loop over many templates used to create a new project
    for dest, temp in [(CONFIGURE_FILE_NAME, 'new_project/configure.py.j2'),
                      ('README.md', 'new_project/README.md.j2'),
                      ('deployments/integration_test/.env', 'new_project/.env.j2'),
                      ('requirements.txt', 'new_project/requirements.txt.j2')]:

        with open(os.path.join(project_config.project_root_dir, dest), "w") as docker_compose_file:
            configure_py_template = get_jinja_env().get_template(temp)
            docker_compose_file.write(configure_py_template.render(
                project_namespace=project_name,
                password=_create_random_password(16),
                version=__version__,
                major_version=int(__version__.split(".", maxsplit=1)[0])
            ))


@create_cmd.command()
def new_service(service_name: str = typer.Argument(None, help="The service name to generate"),
                service_package: Optional[str] = typer.Option(None, '-p', '--package',
                                                              help="Specify the package to create the "
                                                                   "service in. If left empty the first "
                                                                   "package configured will be used."),
                force: Optional[bool] = typer.Option(False, '-f', '--force',
                                                     help="Create service even if if an existing service has the same "
                                                          "name."),
                ):
    # service name
    service_name = service_name.replace(" ", "_").replace("-", '_')
    for letter in service_name:
        if not((letter.isalnum() and (letter.islower() or letter.isnumeric())) or letter == "_"):
            logging.error("Please enter valid name for the service. Only use a-z, 0-9, and '_' .")
            raise typer.Exit(3)
    # service location
    project_config = get_default_context().project_config
    service_package_list = []
    for package in os.listdir(os.path.join(project_config.project_root_dir, "src")):
        if package != project_config.library_package and package != project_config.test_package and \
                os.path.isdir(os.path.join(project_config.project_root_dir, 'src', package)):
            service_package_list.append(package)

    if len(service_package_list) == 0:
        logging.error("No service package found in project to place the service.")
        raise typer.Exit(4)

    # nothing given
    if service_package is None and len(service_package_list) > 1:
        logging.error("More than one service package found. Please choose one manually. "
                      "Detected packages: %s", ", ".join(service_package_list))
        raise typer.Exit(4)

    # package given
    if service_package not in service_package_list:
        logging.error("Package %s not found in project. Found service packages %s.",
                      service_package, ", ".join(service_package_list))
        raise typer.Exit(4)

    service_package = service_package or service_package_list[0]
    service_location = os.path.join(project_config.project_root_dir, "src", service_package, service_name)
    logging.info("The service %s will be created in %s.", service_name, service_location)

    # service package
    if not os.path.isdir(service_location):
        os.makedirs(service_location)
    elif not force:
        logging.warning("Service with same name found. Will not overwrite unless --force is used.")
        raise typer.Exit(5)

    # __init__.py
    with open(os.path.join(service_location, "__init__.py"), "w") as file:
        file.write("\n")

    # class name
    words_list = service_name.split("_")
    service_classname: str = ""
    for word in words_list:
        service_classname = service_classname + word.capitalize()

    # Templates
    for dest, temp in [(MANIFEST_FILENAME, os.path.join('new_service', 'manifest.yaml.j2')),
                       (f'{service_name}_service.py', os.path.join('new_service', 'servicename_service.py.j2')),
                       ('run.py', os.path.join('new_service', '.run.py.j2'))]:
        with open(os.path.join(service_location, dest), "w") as file:
            configure_py_template = get_jinja_env().get_template(temp)
            file.write(configure_py_template.render(
                service_name=service_name,
                service_name_class=service_classname,
                path=f"{service_package}.{service_name}.{service_name}_service"
            ))

    logging.info("Service %s.%s created successfully", service_package, service_name)
