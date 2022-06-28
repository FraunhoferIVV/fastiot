import importlib
import logging
import os

from fastiot.cli.import_configure import import_configure
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import app





if __name__ == '__main__':
    # entry point for fastiot command
    logging.basicConfig(level=logging.INFO)
    default_context = get_default_context()
    default_context.project_config = import_configure()
    _import_commands()
    app()
