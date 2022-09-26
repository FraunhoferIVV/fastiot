import logging
import importlib
import importlib.util
import os
import sys

from fastiot.cli import find_deployments, find_services
from fastiot.cli.constants import CONFIGURE_FILE_NAME, IMPORT_NAME_CONFIGURE_PY
from fastiot.cli.model import ProjectConfig


def import_configure(project_config: ProjectConfig, file_name: str = ''):
    """
    Imports the :file:`configure.py` in the project root (if not specified
    otherwise) and sets project config accordingly.
    """
    file_name = file_name or os.path.join(os.getcwd(), CONFIGURE_FILE_NAME)

    try:
        config = _import_configure_py(file_name)
    except FileNotFoundError:
        logging.warning("No file configure.py found in %s. Trying to continue.", os.path.dirname(file_name))
        return

    for field in ProjectConfig.__fields__:
        if hasattr(config, field):
            setattr(project_config, field, getattr(config, field))

    if project_config.extensions:
        _import_extensions(project_config.extensions)

    if not project_config.deployments:
        project_config.deployments = find_deployments(
            path=project_config.project_root_dir
        )
    if not project_config.services:
        project_config.services = find_services(path=project_config.project_root_dir)


def _import_configure_py(file_name):
    if not os.path.isfile(file_name):
        raise FileNotFoundError(f"Could not find configure file '{file_name}'.")
    spec = importlib.util.spec_from_file_location(IMPORT_NAME_CONFIGURE_PY, file_name)
    config = importlib.util.module_from_spec(spec)
    sys.modules[IMPORT_NAME_CONFIGURE_PY] = config
    spec.loader.exec_module(config)
    return config


def _import_extensions(extensions):
    for extension in extensions:
        try:
            importlib.import_module(extension)
        except ImportError:
            pass  # This will cause some commands to be missed, but a message at this places disturbs autocompletion.
