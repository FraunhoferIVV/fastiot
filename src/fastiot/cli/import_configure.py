import importlib.util
import os
import sys
from typing import Optional

from fastiot.cli import find_deployments, find_services
from fastiot.cli.constants import CONFIGURE_FILE_NAME
from fastiot.cli.model import ProjectConfig


def import_configure(file_name: Optional[str] = None) -> ProjectConfig:
    """ Imports the :file:`configure.py` in the project root (if not specified otherwise) and returns  """
    try:
        config = _import_configure_py(file_name)
    except FileNotFoundError:
        config = ProjectConfig(project_namespace="")

    data = dict()
    for field, options in ProjectConfig.__dict__['__fields__'].items():
        if hasattr(config, field):
            data[field] = getattr(config, field)
        elif options.required:
            raise ValueError(f"Error reading configure.py: Mandatory setting for {field} not found!")
        else:
            data[field] = options.default

    # Use all available configs if not specified otherwise
    project_config = ProjectConfig(**data)
    if project_config.extensions is not None:
        _import_plugin_commands(project_config.extensions)
    project_config.deployments = find_deployments(deployments=data['deployments'],
                                                  path=project_config.project_root_dir)
    if not project_config.services:
        project_config.services = find_services(path=project_config.project_root_dir)

    return project_config


def _import_configure_py(file_name):
    file_name = file_name or os.path.join(os.getcwd(), CONFIGURE_FILE_NAME)
    if not os.path.isfile(file_name):
        raise FileNotFoundError(f"Could not open configure file {file_name} from working directory {os.getcwd()}.")
    spec = importlib.util.spec_from_file_location("config", file_name)
    config = importlib.util.module_from_spec(spec)
    sys.modules["config"] = config
    spec.loader.exec_module(config)
    return config


def _import_plugin_commands(extensions):
    for extension in extensions:
        try:
            importlib.import_module(f'{extension}')
        except ImportError:
            pass  # This will cause some commands to be missed, but a message at this places disturbs autocompletion.
