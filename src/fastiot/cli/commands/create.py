"""
Commands for generating new projects and services.
"""
import getpass
import logging
import os
import random
import shutil
import string
import subprocess
import sys
from glob import glob
from typing import Optional

import typer

from fastiot import __version__
from fastiot.cli.commands.build_lib import update_pyproject_toml
from fastiot.cli.constants import DEPLOYMENTS_CONFIG_DIR, CONFIGURE_FILE_NAME, MANIFEST_FILENAME, \
    DEPLOYMENTS_CONFIG_FILE
from fastiot.cli.helper_fn import get_jinja_env
from fastiot.cli.model import DeploymentConfig
from fastiot.cli.model.infrastructure_service import InfrastructureService
from fastiot.cli.model.project import ProjectContext
from fastiot.cli.typer_app import create_cmd


def _create_random_password(length: int = 16) -> str:
    chars = list(string.ascii_letters + string.digits + "_-.,:%?!*")
    password = [random.choice(chars) for _ in range(length)]
    return "".join(password)


@create_cmd.command()
def new_project(project_name: str = typer.Argument(None, help="The project name to generate"),
                force: bool = typer.Option(False, '-f', '--force',
                                           help="Create project even if an existing project has been found."),
                target_directory: str = typer.Option('.', '-d', '--directory',
                                                     help="The directory the project will be stored"),
                description: str = typer.Option('', '--description',
                                                help="The short description of the project")
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
                      os.path.join(DEPLOYMENTS_CONFIG_DIR, "full"),
                      os.path.join("src", f"{project_name}"),
                      os.path.join("src", f"{project_name}_tests"),
                      os.path.join("src", f"{project_name}_services")]:
        os.makedirs(os.path.join(context.project_root_dir, directory), exist_ok=True)

    # Copy static files like .gitignore
    templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'new_project')
    for src, dest in [('.dockerignore', '.'),
                      ('.gitignore', '.'),
                      ('install.sh', '.'),
                      ('__init__.py', os.path.join("src", f"{project_name}")),
                      ('deployment.yaml', os.path.join(DEPLOYMENTS_CONFIG_DIR, 'integration_test')),
                      ('dummy_test.py', os.path.join("src", f"{project_name}_tests"))]:
        shutil.copy(os.path.join(templates_dir, src), os.path.join(context.project_root_dir, dest))

    # Loop over many templates used to create a new project
    for temp, dest in [('configure.py.j2', CONFIGURE_FILE_NAME),
                       ('README.md.j2', 'README.md'),
                       ('.env.j2', os.path.join('deployments', 'integration_test', '.env')),
                       ('deployment.yaml.j2', os.path.join(DEPLOYMENTS_CONFIG_DIR,
                                                           'production', DEPLOYMENTS_CONFIG_FILE)),
                       ('deployment.yaml.j2', os.path.join(DEPLOYMENTS_CONFIG_DIR, 'full', DEPLOYMENTS_CONFIG_FILE)),
                       ('.env.production.j2', os.path.join(DEPLOYMENTS_CONFIG_DIR, 'production', '.env')),
                       ('.env.production.j2', os.path.join(DEPLOYMENTS_CONFIG_DIR, 'full', '.env'))]:

        # For each potential service create a unique password for the production deployment.
        password_fields = []
        for service in InfrastructureService.all.values():
            password_fields += service.password_env_vars
        env_vars = [f"{f}={_create_random_password(24)}" for f in password_fields]

        with open(os.path.join(context.project_root_dir, dest), "w") as template_file:
            template = get_jinja_env().get_template(os.path.join('new_project', temp))
            template_file.write(template.render(
                project_namespace=project_name,
                env_vars=env_vars,
                user=getpass.getuser()
            ))
    # create toml
    create_toml(path=os.path.join(context.project_root_dir, "pyproject.toml"),
                short_description=description,
                project_name=project_name)

    _create_manifest_in(force=force)

    logging.info("Project created successfully. Check pyproject.toml for correct configuration")


@create_cmd.command()
def new_service(service_name: str = typer.Argument("", help="The service name to generate"),
                service_package: Optional[str] = typer.Option(None, '-p', '--package',
                                                              help="Specify the package to create the "
                                                                   "service in. If left empty and only one package is "
                                                                   "found this one will be used."),
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

    _add_service_to_deployment(service_name)
    logging.info("Service %s.%s created successfully", service_package, service_name)


@create_cmd.command()
def pyproject_toml(description: Optional[str] = typer.Option("", '-d', '--description',
                                                             help="The short description of the project"),
                   force: Optional[bool] = typer.Option(False, '-f', '--force',
                                                        help="Overwrites existing pyproject.toml")):
    """ Creates a new pyproject.toml to build the library."""
    logging.info("Creating a pyproject.toml")

    context = ProjectContext.default
    pyproject_file = os.path.join(context.project_root_dir, "pyproject.toml")

    if os.path.isfile(pyproject_file) and not force:
        logging.error("Not overwriting existing pyproject.toml. Use --force option to overwrite anyways.")
        raise typer.Exit(1)

    create_toml(path=pyproject_file,
                short_description=description,
                project_name=context.project_namespace)

    update_pyproject_toml(update_requirements=True)
    _create_manifest_in(force=force)

    os.rename(os.path.join(context.project_root_dir, "requirements", "requirements.txt"),
              os.path.join(context.project_root_dir, "requirements", "requirements.txt.bak"))
    try:
        os.rename(os.path.join(context.project_root_dir, "setup.py"),
                  os.path.join(context.project_root_dir, "setup.py.bak"))
    except FileNotFoundError:
        pass

    if os.path.isdir(os.path.join(context.project_root_dir, '.git')):  # Add file to git now
        cmd = "git add pyproject.toml"
        subprocess.call(cmd.split(" "), cwd=context.project_root_dir,
                        stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    logging.info("Successfully created pyproject.toml. Please check the file and make adjustments as needed.")
    logging.info("It is recommended to fixate your requirements now by running `fiot extras set-requirements`.")


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
        logging.error("More than one service package found. Please choose one manually using the option `-p`. "
                      "Detected packages: %s", ", ".join(service_package_list))
        raise typer.Exit(4)
    # package given
    if service_package and service_package not in service_package_list:
        logging.error("Package %s not found in project. Found service packages %s.",
                      service_package, ", ".join(service_package_list))
        raise typer.Exit(4)
    service_package = service_package or service_package_list[0]
    return service_package


def _add_service_to_deployment(service_name: str):
    """
    Add the fresh service to the "full" deployment.
    """
    deployment_file = os.path.join(DEPLOYMENTS_CONFIG_DIR, 'full', DEPLOYMENTS_CONFIG_FILE)
    if not os.path.exists(deployment_file):
        logging.debug("No deployment `full` found to add new service automatically. Skipping.")
        return
    deployment = DeploymentConfig.from_yaml_file(deployment_file)

    if service_name not in deployment.services:
        deployment.services[service_name] = None
        deployment.to_yaml_file(deployment_file)


def create_toml(path: str, project_name: str, short_description: str = ""):
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

    fastiot_dependency = f"fastiot>={__version__.split('.dev', 1)[0]}"  # Throw away any .dev… parts
    try:
        fastiot_next_major_version = int(__version__.split(".", maxsplit=1)[0]) + 1
        fastiot_dependency += f",<{fastiot_next_major_version}"
    except ValueError:
        pass

    with open(path, "w") as template_file:
        template = get_jinja_env().get_template("pyproject.toml.j2")
        template_file.write(template.render(
            projectname=project_name,
            authors=getpass.getuser(),
            description=short_description,
            python_version=python_version,
            fastiot_dependency=fastiot_dependency
        ))


def _create_manifest_in(force: bool):
    """ MANIFEST.in includes vcs tracked files *not* to pack into the library source package. """

    context: ProjectContext = ProjectContext.default

    manifest_in_file = os.path.join(context.project_root_dir, 'MANIFEST.in')
    if os.path.isfile(manifest_in_file) and not force:
        logging.debug("MANIFEST.in in %s already exists. Skipping creation, since overwriting has not been forced.",
                      context.project_root_dir)

    excludes = ['docs', DEPLOYMENTS_CONFIG_DIR]
    excludes += [f"src{os.sep}{os.path.basename(e)}" for e in glob(os.path.join(context.project_root_dir, 'src', '*'))]
    excludes = [e for e in excludes if e != f"src{os.sep}{context.library_package}"]
    # We definitely want to have the library, but nothing else

    with open(manifest_in_file, "w") as file:
        file.write("# Exclude some files managed by git when building sdist package\n")
        file.write("# This file has been automatically generated but is not maintained automatically.\n")
        file.write("# If you create any new directories and add them to your VCS, please consider adding them here\n")
        file.write("# or your library source package will grow!\n\n")
        for exclude in excludes:
            file.write(f"recursive-exclude {exclude} *\n")
