"""
Commands for generating new projects and services.
"""
import logging
import os
import random
import shutil
import string
from typing import List, Optional

import typer

from fastiot import __version__
from fastiot.cli.constants import DEPLOYMENTS_CONFIG_DIR, CONFIGURE_FILE_NAME, MANIFEST_FILENAME
from fastiot.cli.helper_fn import get_jinja_env
from fastiot.cli.model.service import InfrastructureService
from fastiot.cli.typer_app import create_cmd
from fastiot.cli.model.project import ProjectContext


def _create_random_password(length: int = 16) -> str:
    chars = list(string.ascii_letters + string.digits + "_-.,:%?!*")
    password = [random.choice(chars) for _ in range(length)]
    return "".join(password)


@create_cmd.command()
def new_project(project_name: str = typer.Argument(None, help="The project name to generate"),
                force: bool = typer.Option(False, '-f', '--force',
                                           help="Create project even if an existing project has been found."),
                target_directory: str = typer.Option('.', '-d', '--directory',
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

    context = ProjectContext.default

    if target_directory.startswith('/'):
        context.project_root_dir = target_directory
    else:
        context.project_root_dir = os.path.join(context.project_root_dir, target_directory)

    # Check for valid project name (no space, no /, …)
    project_name = project_name.replace(" ", "_").replace("-", '_')
    for letter in project_name:
        if not (letter.isalnum() or letter == "_" or letter == "."):
            logging.error("Please enter valid Name. Only use a-z, A-Z, 0-9, '.' and '_' .")
            raise typer.Exit(3)
    logging.info("The project %s will be created in %s", project_name, context.project_root_dir)

    # Create necessary directories
    if not os.path.exists(context.project_root_dir):
        os.makedirs(context.project_root_dir)
    for directory in [os.path.join(DEPLOYMENTS_CONFIG_DIR, "integration_test"),
                      os.path.join(DEPLOYMENTS_CONFIG_DIR, "production"),
                      os.path.join("src", f"{project_name}"),
                      os.path.join("src", f"{project_name}_tests"),
                      os.path.join("src", f"{project_name}_services")]:
        os.makedirs(os.path.join(context.project_root_dir, directory), exist_ok=True)

    # Copy static files like .gitignore
    templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'new_project')
    for src, dest in [('.dockerignore', '.'),
                      ('.gitignore', '.'),
                      ('install.sh', '.'),
                      ('deployment.yaml', os.path.join(DEPLOYMENTS_CONFIG_DIR, 'integration_test')),
                      ('dummy_test.py', os.path.join("src", f"{project_name}_tests"))]:
        shutil.copy(os.path.join(templates_dir, src), os.path.join(context.project_root_dir, dest))

    # Loop over many templates used to create a new project
    for dest, temp in [(CONFIGURE_FILE_NAME, 'new_project/configure.py.j2'),
                       ('README.md', 'new_project/README.md.j2'),
                       ('deployments/integration_test/.env', 'new_project/.env.j2'),
                       ('deployments/production/.env', 'new_project/.env.production.j2'),
                       ('requirements.txt', 'new_project/requirements.txt.j2')]:

        # For each potential service create a unique password for the production deployment.
        password_fields = []
        for service in InfrastructureService.all.values():
            password_fields += service.password_env_vars
        env_vars = [f"{f}={_create_random_password(24)}" for f in password_fields]

        with open(os.path.join(context.project_root_dir, dest), "w") as template_file:
            template = get_jinja_env().get_template(temp)
            template_file.write(template.render(
                project_namespace=project_name,
                version=__version__,
                major_version=int(__version__.split(".", maxsplit=1)[0]),
                env_vars=env_vars
            ))

    logging.info("Project created successfully")


@create_cmd.command()
def new_service(service_name: str = typer.Argument("", help="The service name to generate"),
                service_package: Optional[str] = typer.Option(None, '-p', '--package',
                                                              help="Specify the package to create the "
                                                                   "service in. If left empty the first "
                                                                   "package configured will be used."),
                force: Optional[bool] = typer.Option(False, '-f', '--force',
                                                     help="Create service even if if an existing service has the same "
                                                          "name."),
                ):
    """ Create a new service with some method stubs for further programming. """
    # service name
    service_name = _sanitize_service_name(service_name)
    # service location
    context = ProjectContext.default
    service_package = _find_service_package(context, service_package)
    service_location = os.path.join(context.project_root_dir, "src", service_package, service_name)
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


def _sanitize_service_name(service_name):
    service_name = service_name.replace(" ", "_").replace("-", '_')
    for letter in service_name:
        if not ((letter.isalnum() and (letter.islower() or letter.isnumeric())) or letter == "_"):
            logging.error("Please enter valid name for the service. Only use a-z, 0-9, and '_' .")
            raise typer.Exit(3)
    return service_name


def _find_service_package(project_config, service_package):
    """
    Find *the* package to place the service if not defined. Raise errors when no or to many packages are possible.
    """
    service_package_list = []
    for package in os.listdir(os.path.join(project_config.project_root_dir, "src")):
        if package != project_config.library_package and package != project_config.test_package and \
                os.path.isdir(os.path.join(project_config.project_root_dir, 'src', package)):
            service_package_list.append(package)
    if len(service_package_list) == 0:
        logging.error("No service package found in project to place the service.")
        raise typer.Exit(4)
    # nothing given
    if not service_package and len(service_package_list) > 1:
        logging.error("More than one service package found. Please choose one manually. "
                      "Detected packages: %s", ", ".join(service_package_list))
        raise typer.Exit(4)
    # package given
    if service_package and service_package not in service_package_list:
        logging.error("Package %s not found in project. Found service packages %s.",
                      service_package, ", ".join(service_package_list))
        raise typer.Exit(4)
    service_package = service_package or service_package_list[0]
    return service_package
