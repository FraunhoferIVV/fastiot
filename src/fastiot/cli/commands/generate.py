"""
Commands for generating new projects and services.
"""
import logging
import os
from typing import Optional

import typer

from fastiot.cli.helper_fn import get_jinja_env
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import create_cmd


@create_cmd.command()
def new_project(project_name: str = typer.Argument(None, help="The project name to generate"),
                target_dir: str = typer.Option('.', '-d', '--dir', help="Specify the dir to generate the new project in."),
                force: Optional[bool] = typer.Option(False, '-f', '--force',
                                                     help="Create project even if an existing project has been found.")
                ):
    """
    Function to create a new project with its directory structure and all needed files for a quick start.

    You may use the the function `new-service` afterwards to create your first service stubs.
    """
    logging.warning("This method has not yet been fully implemented")

    project_config = get_default_context().project_config
    if project_config.project_namespace != "" and not force:
        logging.error("An existing project configuration has been found with project namespace %s. "
                      "To force overwriting this you may use the --force argument.",
                      get_default_context().project_config.project_namespace)
        raise typer.Exit(2)

    if target_dir.startswith('/'):
        project_config.project_root_dir = target_dir
    else:
        project_config.project_root_dir = os.path.join(project_config.project_root_dir, target_dir)

    if not os.path.exists(project_config.project_root_dir):
        os.makedirs(project_config.project_root_dir)

    # TODO: Check for valid project name (no space, no /, …)
    project_name = project_name.replace(" ", "_").replace("-", '_')

    logging.info("Creating new project with namespace `%s`", project_name)

    # TODO: Create necessary directories

    # TODO: Loop over many templates used to create a new project
    with open(os.path.join(project_config.project_root_dir, 'configure.py'), "w") as docker_compose_file:
        configure_py_template = get_jinja_env().get_template('new_project/configure.py.j2')
        docker_compose_file.write(configure_py_template.render(
            project_namespace=project_name
        ))

    # TODO: Copy static files like .gitignore


@create_cmd.command()
def new_service(service_name: str = typer.Argument(None, help="The project name to generate"),
                service_package: Optional[str] = typer.Option(default=None, help="Specify the package to create the "
                                                                                 "service in. If left empty the first "
                                                                                 "package configured will be used.")):
    logging.error("This method has not yet been implemented")
    raise typer.Exit(1)
