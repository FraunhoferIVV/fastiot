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
        print(target_directory)
        raise typer.Exit(2)

    project_config = get_default_context().project_config

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

    logging.warning("This method has not yet been fully implemented")


@create_cmd.command()
def new_service(service_name: str = typer.Argument(None, help="The service name to generate"),
                service_package: Optional[str] = typer.Option(None, '-p', '--package',
                                                              help="Specify the package to create the "
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
        service_package = '/home/sieber/'
        project_config = get_default_context().project_config

        print(project_config.test_package)
        print(project_config.project_root_dir)
        print(project_config.library_package)
        print(project_config.services)

        list_src_packages = os.listdir(os.path.join(project_config.project_root_dir, "src"))
        if list_src_packages.__contains__(project_config.library_package):
            list_src_packages.remove(project_config.library_package)
        if list_src_packages.__contains__(project_config.test_package):
            list_src_packages.remove(project_config.test_package)
        if len(list_src_packages) > 1:
            logging.info("more than one service package pleas choose Manual")
        elif list_src_packages == 1:
            print("Destination folder: " + list_src_packages[0])
        else:
            logging.info("No service package found")












    service_location = os.path.join(service_package, service_name)
    os.mkdir(service_location)
    # __init__.py
    open(os.path.join(service_location, "__init__.py"), "w")

    # Templates
    for dest, temp in [('manifest.ymal','new_service/manifest.yaml.j2'),
                       (f'{service_name}_service.py', 'new_service/servicename_service.py.j2'),
                       ('run.py', 'new_service/.run.py.j2')]:
        with open(os.path.join(service_location, dest), "w") as file:
            configure_py_template = get_jinja_env().get_template(temp)
            file.write(configure_py_template.render(
                service_name=service_name,
                service_name_camel=service_name.capitalize()
            ))


    logging.error("This method has not yet been implemented")
    raise typer.Exit(1)
