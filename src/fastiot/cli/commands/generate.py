import logging
import sys
from typing import Optional

import typer

from fastiot.cli.typer_app import create_cmd


@create_cmd.command()
def new_project(project_name: str = typer.Argument(None, help="The project name to generate")):
    logging.error("This method has not yet been implemented")
    sys.exit(-1)


@create_cmd.command()
def new_module(module_name: str = typer.Argument(None, help="The project name to generate"),
               module_package: Optional[str] = typer.Option(default=None, help="Specify the package to create the "
                                                                               "module in. If left empty the first "
                                                                               "package configured will be used.")):
    logging.error("This method has not yet been implemented")
    sys.exit(-1)
