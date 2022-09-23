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
from fastiot.cli.constants import DEPLOYMENTS_CONFIG_DIR, CONFIGURE_FILE_NAME
from fastiot.cli.helper_fn import get_jinja_env
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import create_cmd


def new_password(length: int) -> str:

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


    # TODO: Check for valid project name (no space, no /, …)

    project_name = project_name.replace(" ", "_").replace("-", '_')
    for letter in project_name:
        if not (letter.isalnum() or letter == "_" or letter == "."):
            logging.error("Please enter valid Name. Only use a-z, A-Z, 0-9, '.' and '_' .")
            raise typer.Exit(3)
    logging.info(f"the project {project_name} will be created in {project_config.project_root_dir}")


    # TODO: Create necessary directories
    if not os.path.exists(project_config.project_root_dir):
        os.makedirs(project_config.project_root_dir)
    for directory in [
                      os.path.join(DEPLOYMENTS_CONFIG_DIR, "integration_test"),
                      os.path.join("src", f"{project_name}_lib"),
                      os.path.join("src", f"{project_name}_tests"),
                      os.path.join("src", f"{project_name}_services")]:
        os.makedirs(os.path.join(project_config.project_root_dir, directory), exist_ok=True)

    # TODO: Copy static files like .gitignore
    templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'new_project')
    for src, dest in [('.dockerignore', '.'),
                      ('.gitignore', '.'),
                      ('install.sh', '.'),
                      ('deployment.yaml', os.path.join(DEPLOYMENTS_CONFIG_DIR, 'integration_test'))]:
        shutil.copy(os.path.join(templates_dir, src), os.path.join(project_config.project_root_dir, dest))


    # shutil.copytree(os.path.join(project_config.project_root_dir, 'src/fastiot/cli/templates/new_project/.run'),
        # os.path.join(project_config.project_root_dir, '.run'))


    # TODO: Loop over many templates used to create a new project
    for dest,temp in [(CONFIGURE_FILE_NAME, 'new_project/configure.py.j2'),
                      ('README.md', 'new_project/README.md.j2'),
                      ('deployments/integration_test/.env', 'new_project/.env.j2'),
                      ('requirements.txt', 'new_project/requirements.txt.j2')]:

        with open(os.path.join(project_config.project_root_dir, dest), "w") as docker_compose_file:
            configure_py_template = get_jinja_env().get_template(temp)
            docker_compose_file.write(configure_py_template.render(
                project_namespace=project_name,
                password=new_password(16),
                version=__version__,
                major_version=int(__version__.split(".")[0])
            ))


@create_cmd.command()
def new_service(service_name: str = typer.Argument(None, help="The service name to generate"),
                service_package: Optional[str] = typer.Option(None, '-p', '--package',
                                                              help="Specify the package to create the "
                                                                   "service in. If left empty the first "
                                                                   "package configured will be used."),
                force: Optional[bool] = typer.Option(False, '-f', '--force',
                                         help="Create service even if if an existing service has the same name."),
                ):
    # service name
    service_name = service_name.replace(" ", "_").replace("-", '_')
    for letter in service_name:
        if not((letter.isalnum() and (letter.islower() or letter.isnumeric())) or letter == "_" or letter == "."):
            logging.error("Please enter valid Name. Only use a-z, 0-9, '.' and '_' .")
            raise typer.Exit(3)
    # service location
    project_config = get_default_context().project_config
    service_package_list = []
    # nothing given
    if service_package is None:
        for package in os.listdir(os.path.join(project_config.project_root_dir, "src")):
            if "service" in package:
                service_package_list.append(package)

        if len(service_package_list) == 0:
            logging.warning("no service package found")
            raise typer.Exit(4)
        elif len(service_package_list) == 1:
            service_location = os.path.join(os.path.join(project_config.project_root_dir, "src", service_package_list[0]
                                                         , service_name))
        else:
            logging.warning("more than one service package please choose manual")
            print(service_package_list)
            raise typer.Exit(4)
    # package given
    else:
        for package in os.listdir(os.path.join(project_config.project_root_dir, "src")):
            if service_package == package:
                service_package_list.append(package)

        if len(service_package_list) == 1:
            service_location = os.path.join(os.path.join(project_config.project_root_dir, "src", service_package_list[0]
                                                         , service_name))
            service_package = service_package_list[0]
        else:
            logging.warning("package could not be found")
            raise typer.Exit(4)

    logging.info(f"the service {service_name} will be created in {service_location}")

    # service package
    if not (os.path.isdir(service_location)):
        os.makedirs(service_location)
    elif not force:
        logging.warning("service with same name found")
        raise typer.Exit(5)

    # __init__.py
    open(os.path.join(service_location, "__init__.py"), "w")

    # Templates
    for dest, temp in [('manifest.ymal', os.path.join('new_service', 'manifest.yaml.j2')),
                       (f'{service_name}_service.py', os.path.join('new_service', 'servicename_service.py.j2')),
                       ('run.py', os.path.join('new_service', '.run.py.j2'))]:
        with open(os.path.join(service_location, dest), "w") as file:
            configure_py_template = get_jinja_env().get_template(temp)
            file.write(configure_py_template.render(
                service_name=service_name,
                service_name_camel=service_name.capitalize(),
                path=f"{service_package}.{service_name}"
            ))
